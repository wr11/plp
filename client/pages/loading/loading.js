// pages/loading/loading.js

let app = getApp()

Page({
  /**
   * 页面的初始数据
   */
  data: {
    progress_percent : app.globalData.progress_percent
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    app.connectcb = this.updateProgress

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

  updateProgress(progress) {
    this.setData({progress_percent:progress})
  },

  finishLoad(){
    wx.showToast({
      icon: "success",
      title: '加载完成',
    })
    setTimeout(this.finishLoad2, 2000)
  },

  finishLoad2(){
    let ret = app.InitUserInfo()
    if (!ret){
      wx.redirectTo({
        url: '/pages/login/login',
      })
    }
    else{
      wx.redirectTo({
        url: '/pages/game/game',
      })
    }
  }
})