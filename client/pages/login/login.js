// pages/login/login.js
import {GAME_NAME} from "../../utils/globalconst.js"
import {NetPack} from '../../utils/netpackage.js'

let app = getApp()

Page({

  /**
   * 页面的初始数据
   */
  data: {
    gamename: GAME_NAME,
    user_phone: "",
    user_password: ""
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
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
  onShow() {
    wx.hideHomeButton({
      success: (res) => {},
    })
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

  getPhone: function (res) {
    this.setData({
      user_phone: res.detail.value
    })
  },
  getPassword: function (res) {
    this.setData({
      user_password: res.detail.value
    })
  },
  clickLogin: function () {
    let phone = this.data.user_phone;
    let password = this.data.user_password;
    if (phone == "") {
      wx.showToast({
        icon: "none",
        title: '请输入手机号',
      })
      return
    }
    if (password == "") {
      wx.showToast({
        icon: "none",
        title: '请输入密码',
      })
      return
    }
    if (!this.validPhone(phone)) {
      wx.showToast({
        icon: "none",
        title: '请正确输入手机号码',
      })
      return
    }
    console.log("通过验证")
  },

  validPhone: function (phone) {
    if(!(/^1[3456789]\d{9}$/.test(phone))){
      return false
    }
    return true
  }
})