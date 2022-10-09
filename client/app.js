import {SERVER_IP, SERVER_PORT} from '/utils/globalconst.js'

App({

  /**
   * 当小程序初始化完成时，会触发 onLaunch（全局只触发一次）
   */
  onLaunch: function () {
    this.MakeConnection()
  },

  /**
   * 当小程序启动，或从后台进入前台显示，会触发 onShow
   */
  onShow: function (options) {
    
  },

  /**
   * 当小程序从前台进入后台，会触发 onHide
   */
  onHide: function () {
    
  },

  /**
   * 当小程序发生脚本错误，或者 api 调用失败时，会触发 onError 并带上错误信息
   */
  onError: function (msg) {
    
  },

  globalData:{
    userinfo : null,
    tcpconn : null,
    connectstate : false
  },

  MakeConnection: function(){
    const oTcp = wx.createTCPSocket()
    this.globalData.tcpconn = oTcp
    oTcp.connect({
        address: SERVER_IP,
        port: SERVER_PORT
    })
    oTcp.onConnect(() => {
        console.log("connect to server success",SERVER_IP,SERVER_PORT)
        wx.showToast({
            title: '服务器连接成功',
            icon: 'success',
            duration: 2000
        })
        this.globalData.connectstate = true
      })
    oTcp.onMessage((message, remoteInfo, localInfo) => {
        console.log("receive message from server",message, remoteInfo, localInfo)
    })
    oTcp.onClose(() => {
        console.log("disconnected with server",SERVER_IP,SERVER_PORT)
        wx.showToast({
            title: '与服务器断开连接',
            icon: 'error',
            duration: 2000
        })
        this.globalData.connectstate = false
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

  FillUserInfo: function(iPhoneNum){
    var userinfo = {
      phone: iPhoneNum
    }
    this.globalData.userinfo = userinfo

    wx.setStorageSync('userinfo', this.globalData.userinfo)
  },

  InitUserInfo: function(){
    var res = wx.getStorageSync('userinfo')
    if (res){
      this.globalData.userinfo = res
      return true
    } else {
      return false
    }
  },

  GetUserInfo: function(){
    return this.globalData.userinfo
  },

  RemoveUserInfo: function(){
    this.globalData.userinfo = null

    wx.removeStorageSync('userinfo')
  }
})
