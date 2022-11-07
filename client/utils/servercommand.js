//用于处理单独由服务器发起协议（客户端发起但需要服务器回调的协议不算）

import {PROTOCOL} from 'protocol.js'
import {NetPack} from 'netpackage.js'

export function execServerCommand(header, oNetPack){
  if (header == PROTOCOL.S2C_SHOWTOAST){
    let sDesc = NetPack.UnpackS(oNetPack)
    let sIcon = NetPack.UnpackS(oNetPack)
    let sMsg = NetPack.UnpackS(oNetPack)
    let iDuration = NetPack.UnpackInt16(oNetPack)
    let bMask = NetPack.UnpackBool(oNetPack)
    let bNeedCallBack = NetPack.UnpackBool(oNetPack)
    showToast(sDesc, sIcon, sMsg, iDuration, bMask, bNeedCallBack)
    return
  }
  if (header == PROTOCOL.S2C_SHOWMODAL){
    let sDesc = NetPack.UnpackS(oNetPack)
    let sTitle = NetPack.UnpackS(oNetPack)
    let sContent = NetPack.UnpackS(oNetPack)
    let sConfirmText = NetPack.UnpackS(oNetPack)
    let sConfirmColor = NetPack.UnpackS(oNetPack)
    let bShowCancel = NetPack.UnpackBool(oNetPack)
    let sCancelText = NetPack.UnpackS(oNetPack)
    let sCancelColor = NetPack.UnpackS(oNetPack)
    let bEditable = NetPack.UnpackBool(oNetPack)
    let sPlaceholderText = NetPack.UnpackS(oNetPack)
    let bNeedCallBack = NetPack.UnpackBool(oNetPack)
    showModal(sDesc, sTitle, sContent, sConfirmText, sConfirmColor, bShowCancel, sCancelText, sCancelColor, bEditable, sPlaceholderText, bNeedCallBack)
    return
  }
  if (header == PROTOCOL.S2C_OFFLINE){
    clientOffline()
    return
  }
}

function showToast(sDesc, sIcon, sMsg, iDuration, bMask, bNeedCallBack){
  wx.showToast({
    title: sMsg,
    icon: sIcon,
    duration: iDuration,
    mask: bMask,
    success: function(res){
      if (!bNeedCallBack){
        return
      }
      oNetPack = NetPack.PacketPrepare(PROTOCOL.C2S_TOASTCB)
      NetPack.PacketAddInt8(1, oNetPack)
      NetPack.PacketAddS(sDesc, oNetPack)
      NetPack.PacketSend(oNetPack)
    }
  })
}

function showModal(sDesc, sTitle, sContent, sConfirmText, sConfirmColor, bShowCancel, sCancelText, sCancelColor, bEditable, sPlaceholderText, bNeedCallBack){
  wx.showModal({
    title: sTitle,
    content: sContent,
    showCancel: bShowCancel,
    cancelText: sCancelText,
    cancelColor: sCancelColor,
    confirmText: sConfirmText,
    confirmColor: sConfirmColor,
    editable: bEditable,
    placeholderText: sPlaceholderText,
    success: function(res){
      if (!bNeedCallBack){
        return
      }
      let sContent = res.content
      if (sContent == null){
        sContent = ""
      }
      let bComfirm = res.confirm
      let bCancel = res.cancel
      let oNetPack = NetPack.PacketPrepare(PROTOCOL.C2S_MODALCB)
      NetPack.PacketAddInt8(2, oNetPack)
      NetPack.PacketAddS(sDesc, oNetPack)
      NetPack.PacketAddS(sContent, oNetPack)
      NetPack.PacketAddBool(bComfirm, oNetPack)
      NetPack.PacketAddBool(bCancel, oNetPack)
      NetPack.PacketSend(oNetPack)
    },
  })
}

function clientOffline(){
  let app = getApp()
  if (!app.getConnectState()) {
    return
  }
  let conn = app.getTcpConnect()
  conn.close()
}