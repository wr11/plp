// pages/loading/loading.js

import {SERVER_IP, SERVER_PORT} from '../../utils/globalconst.js'
import {NetPack, netCommand} from '../../utils/netpackage.js'
import {PROTOCOL} from '../../utils/protocol.js'
import {LOGIN_ERRCODE} from '../../utils/globalconst.js'

let app = getApp()

Page({
  /**
   * 页面的初始数据
   */
  data: {
    progress_percent : 0,
    wxlogincode : "",
    hidden_gm : true,
    animation_plp : {},
    animation_checkin : {},
    hidden_loading : false,
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onShow(options) {
    wx.hideHomeButton({
      success: (res) => {},
    })
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady() {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onLoad() {
    this.animation_plp = wx.createAnimation({
      duration: 800,
      timingFunction: "ease"
    })
    this.animation_checkin = wx.createAnimation({
      duration: 500,
      timingFunction: "ease"
    })
    this.drawPlpAnimation()
    this.drawCheckInAnimation()
    wx.hideHomeButton({
      success: (res) => {},
    })
    this.MakeConnection()
  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide() {
    wx.hideHomeButton({
      success: (res) => {},
    })
  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload() {
    wx.hideHomeButton({
      success: (res) => {},
    })
  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh() {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom() {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage() {

  },

  drawPlpAnimation: function(){
    let flag = true
    setInterval(() => {
      if (flag) {
        this.animation_plp.translateY(10).step()
      } else{
        this.animation_plp.translateY(0).step()
      }
      flag = !flag
      this.setData({
        animation_plp: this.animation_plp.export()
      })
    }, 800)
  },

  drawCheckInAnimation: function(){
    let flag = true
    setInterval(() => {
      if (flag) {
        this.animation_checkin.scale(0.8).step()
      } else{
        this.animation_checkin.scale(1).step()
      }
      flag = !flag
      this.setData({
        animation_checkin: this.animation_checkin.export()
      })
    }, 500)
  },

  MakeConnection: function(){
    this.updateProgress(10)
    let that = this
    const oTcp = wx.createTCPSocket()
    app.globalData.tcpconn = oTcp
    oTcp.connect({
        address: SERVER_IP,
        port: SERVER_PORT
    })
    oTcp.onConnect(() => {
        console.log("connect to server success",SERVER_IP,SERVER_PORT)
        app.globalData.connectstate = true
        let oNetPack = NetPack.PacketPrepare(PROTOCOL.CS_HELLO, that.onServerHello)
        NetPack.PacketSend(oNetPack)
        setInterval(
          function(){
            console.log("check operate",app.globalData.noOperate,app.getConnectState())
            if (app.globalData.noOperate && app.getConnectState()){
              let conn = app.getTcpConnect()
              conn.close()
            }
            app.globalData.noOperate = true
          },
          1000 * 60 * 20
        )
        app.globalData.noOperate = true
      })
    oTcp.onMessage((message) => {
        let oNetPack = NetPack.UnpackPrepare(message.message)
        let header = NetPack.UnpackInt16(oNetPack)
        netCommand(header, oNetPack)
        app.globalData.noOperate = false
    })
    oTcp.onClose(() => {
        console.log("disconnected with server",SERVER_IP,SERVER_PORT)
        wx.showToast({
            title: '服务器连接丢失',
            icon: 'error',
            duration: 2000
        })
        app.globalData.connectstate = false
    })
    oTcp.onError((res) => {
        console.log("connect to server failed",SERVER_IP,SERVER_PORT)
        wx.showToast({
            title: '服务器维护中，请稍后再试',
            icon: 'error',
            duration: 2000
        })
    })
  },

  onServerHello(state, oNetPack){
    if (state == -1){
      wx.showToast({
        icon: "error",
        title: '服务器连接异常，请重试',
      })
      return
    }
    let iServerState = NetPack.UnpackInt8(oNetPack)
    if (iServerState == 0){
      wx.showToast({
        icon: "error",
        title: '服务器维护',
      })
      return
    }

    this.updateProgress(25)
    this.checkNeedLoginWX()
  },

  checkNeedLoginWX: function(){
    let that = this
    let userInfo = app.getUserInfo()
    if (!userInfo){
      this.WXLogin()
      return
    }
    wx.checkSession({
      success: function(){
        that.serverLogin()
        return
      },
      fail: function(){
        that.WXLogin()
        return
      }
    })
  },
    
  WXLogin: function(){
    this.getWXLoginCode(this.getAppFlag)
  },

  getAppFlag(code){
    this.setData({wxlogincode: code})
    this.updateProgress(50)
    let oNetPack = NetPack.PacketPrepare(PROTOCOL.CS_GETAPPFLAG, this.getOpenID)
    NetPack.PacketSend(oNetPack)
  },

  getOpenID(state, oNetPack){
    if (state == -1){
      wx.showToast({
        icon: "error",
        title: '服务器连接异常，请重试',
      })
      return
    }
    let that = this
    let appID = NetPack.UnpackS(oNetPack)
    let secretKey = NetPack.UnpackS(oNetPack)
    wx.request({
      url: "https://api.weixin.qq.com/sns/jscode2session?appid=" + appID + "&secret=" + secretKey + "&js_code=" + this.data.wxlogincode + "&grant_type=authorization_code",
      success: function(result){
        that.handleOpenIDSSKey(result.data.session_key, result.data.openid)
      },
      fail: function(result){
        wx.showToast({
          icon: "error",
          title: '获取openID失败，请重试',
        })
      }
    })
  },

  handleOpenIDSSKey(sessionKey, openID){
    let userInfo = {
      sessionKey : sessionKey,
      openID : openID
    }
    app.initUserInfo(userInfo)
    this.serverLogin()
  },

  getWXLoginCode(cbFunc){
    wx.login({
      timeout: 5000,
      success: function(result){
        cbFunc(result.code)
      },
      fail: function(result){
        wx.showToast({
          icon: "error",
          title: '微信登录失败，请稍后重试'
        })
      }
    })
  },

  updateProgress(progress) {
    console.log("progress",progress)
    this.setData({progress_percent:progress})
  },

  serverLogin(){
    this.updateProgress(70)
    let openID = app.getUserInfo().openID
    let oNetPack = NetPack.PacketPrepare(PROTOCOL.CS_LOGIN, this.serverLoginCB)
    NetPack.PacketAddS(openID, oNetPack)
    NetPack.PacketSend(oNetPack)
  },

  serverLoginCB(state, oNetPack){
    if (state == -1){
      wx.showToast({
        icon: "error",
        title: '服务器连接异常，请重试',
      })
      return
    }
    let iRet = NetPack.UnpackInt8(oNetPack)
    console.log("login ret ------------", iRet)
    if (iRet > 10){
      let iNewRet = iRet - 10
      let sMsg = LOGIN_ERRCODE[iNewRet]
      wx.showToast({
        icon: "none",
        title: sMsg
      })
      return
    }
    let bAuth = NetPack.UnpackBool(oNetPack)
    console.log("auth ------------", bAuth)
    app.globalData.auth = bAuth

    this.setData({hidden_gm: !app.globalData.auth})
    this.updateProgress(100)
  },

  finishLoad(){
    if (this.data.progress_percent == 100){
      setTimeout(this.finishLoad2, 300)
      this.setData({hidden_loading : true})
    }
  },

  finishLoad2(){
    wx.showToast({
      icon: "success",
      title: '加载完成',
    })
    //setTimeout(this.GotoGame, 200)
  },

  GotoGame(){
    wx.redirectTo({
      url: '../main/main',
    })
  },

  GetAPZ(){
    console.log("===get a pz")
    let oNetPack = NetPack.PacketPrepare(PROTOCOL.CS_GETPZ, this.GetPZ)
    NetPack.PacketAddInt8(12, oNetPack)
    NetPack.PacketAddS("111", oNetPack)
    NetPack.PacketSend(oNetPack)
  },

  GetPZ(state, oNetPack){
    if (state == -1){
      console.log("fail")
      return
    }
    let len = NetPack.UnpackInt8(oNetPack)
    let dict = {}
    for (let i=0; i<len; i++)
    {
      let key = NetPack.UnpackS(oNetPack)
      let value = NetPack.UnpackS(oNetPack)
      dict[key] = value
    }
    console.log("=====dict", dict)
  },

  openGM(){
    wx.navigateTo({
      url: '../gm/gm',
    })
  }
})