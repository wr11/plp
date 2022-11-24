// pages/main/main.ts

import {NetPack} from '../../utils/netpackage.js'
import {PROTOCOL} from '../../utils/protocol.js'

let app = getApp()

Page({

  /**
   * 页面的初始数据
   */
  data: {
    text : "sss",
    hidden_gm : !app.globalData.auth,
  },

  SetBottle: function(e) {
    console.log("1111111")
    wx.navigateTo({
      url: "/pages/content/content"
    })
  },

  getPlp: function(){
    let oNetPack = NetPack.PacketPrepare(PROTOCOL.CS_GETPZ, this.showPlpInfo)
    NetPack.PacketSend(oNetPack)
  },

  showPlpInfo: function(state, oNetPack) {
    if (state == -1){
      console.log("fail")
      return
    }
    let data = NetPack.UnpackJSON(oNetPack)
    let sData = JSON.stringify(data)
    this.setData({text:sData})
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad() {

  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady() {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {
    this.setData({hidden_gm : !app.globalData.auth,})
  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide() {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload() {

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

  openGM(){
    wx.navigateTo({
      url: '../gm/gm',
    })
  }
})