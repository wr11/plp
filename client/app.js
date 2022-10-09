App({

  /**
   * 当小程序初始化完成时，会触发 onLaunch（全局只触发一次）
   */
  onLaunch: function () {
    
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
    userinfo : null
  },

  FillUserInfo: function(iPhoneNum){
    var userinfo = {
      phone: iPhoneNum
    }
    this.globalData.setData({
      userinfo: userinfo
    })

    wx.setStorageSync('userinfo', this.globalData.userinfo)
  },

  InitUserInfo: function(){
    var res = wx.getStorageSync('userinfo')
    if (res){
      this.globalData.setData({
        userinfo: res
      })
      return true
    } else {
      return false
    }
  },

  GetUserInfo: function(){
    return this.globalData.userinfo
  },

  RemoveUserInfo: function(){
    this.globalData.setData({
      userinfo: null
    })

    wx.removeStorageSync('userinfo')
  }
})
