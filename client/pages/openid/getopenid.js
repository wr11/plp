// pages/openid/getopenid.js
Page({

  /**
   * 页面的初始数据
   */
  data: {
    code : "",
    openid : ""
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {

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

  getOpenID(){
    let that = this
    wx.login({
      timeout : 5000,
      success: function (result) {
        console.log(result)
        that.setData({code : result.code})
        that.trueGetOpenID()
      },
      fail: function(result) {
        wx.showToast({
          title: '登录失败，请稍后再试',
        })
      }
    })
    return
  },

  trueGetOpenID(){
    return
  }
})