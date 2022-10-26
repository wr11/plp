//用于处理单独由服务器发起协议（客户端发起但需要服务器回调的协议不算）

import {PROTOCOL} from 'protocol.js'
import {NetPack} from 'netpackage.js'

export function execServerCommand(header, oNetPack){
  if (header == PROTOCOL.S2C_SHOWTOAST){
    let sDesc = NetPack.UnpackString(oNetPack)
    let sIcon = NetPack.UnpackString(oNetPack)
    let sMsg = NetPack.UnpackString(oNetPack)
    let iDuration = NetPack.UnpackInt16(oNetPack)
    let bMask = NetPack.UnpackBool(oNetPack)
    let bNeedCallBack = NetPack.UnpackBool(oNetPack)
    showToast(sDesc, sIcon, sMsg, iDuration, bMask, bNeedCallBack)
    return
  }
  if (header == PROTOCOL.S2C_SHOWMODAL){
    let sDesc = NetPack.UnpackString(oNetPack)
    let sTitle = NetPack.UnpackString(oNetPack)
    let sContent = NetPack.UnpackString(oNetPack)
    let sConfirmText = NetPack.UnpackString(oNetPack)
    let sConfirmColor = NetPack.UnpackString(oNetPack)
    let bShowCancel = NetPack.UnpackBool(oNetPack)
    let sCancelText = NetPack.UnpackString(oNetPack)
    let sCancelColor = NetPack.UnpackString(oNetPack)
    let bEditable = NetPack.UnpackBool(oNetPack)
    let sPlaceholderText = NetPack.UnpackString(oNetPack)
    let bNeedCallBack = NetPack.UnpackBool(oNetPack)
    showModal(sDesc, sTitle, sContent, sConfirmText, sConfirmColor, bShowCancel, sCancelText, sCancelColor, bEditable, sPlaceholderText, bNeedCallBack)
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
      NetPack.PacketAddI(1, oNetPack)
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
      NetPack.PacketAddI(2, oNetPack)
      NetPack.PacketAddS(sDesc, oNetPack)
      NetPack.PacketAddS(sContent, oNetPack)
      NetPack.PacketAddBool(bComfirm, oNetPack)
      NetPack.PacketAddBool(bCancel, oNetPack)
      NetPack.PacketSend(oNetPack)
    },
  })
}