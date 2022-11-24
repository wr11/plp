// pages/content/content.ts

import {NetPack} from '../../utils/netpackage.js'
import {PROTOCOL} from '../../utils/protocol.js'

let app = getApp()

Page({

  /**
   * 页面的初始数据
   */
  data: {
    title: "",
    tag: "",
    content: "",
    hidden_gm : !app.globalData.auth,
  },

  GetTitle: function(e) {
    let sTitle = e.detail.value;
    this.setData({
      title: sTitle 
    })
  },

  GetTag: function(e) {
    let v = e.detail.value;
    this.setData({
      tag: v 
    })
  },

  GetContent: function(e) {
    let v = e.detail.value;
    this.setData({
      content: v 
    })
  },
  

  EnsurePack: function(e) {
    console.log(this.data.title)
    console.log(this.data.tag)
    console.log(this.data.content)
    if (this.data.title.length == 0 || this.data.tag == 0 || this.data.content == 0) {
      wx.showToast({
        title: "请填写内容",
        icon: "none",
      })
      return
    }
    let data = {
      "title" : this.data.title,
      "tag" : this.data.tag,
      "content" : this.data.content
    }
    this.C2SSendPlp(data)
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

  C2SSendPlp(data) {
    let oNetPack = NetPack.PacketPrepare(PROTOCOL.C2S_SENDPLP)
    NetPack.PacketAddJSON(data, oNetPack)
    NetPack.PacketSend(oNetPack)
  },

  openGM(){
    wx.navigateTo({
      url: '../gm/gm',
    })
  }
})