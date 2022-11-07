/*
网络数据打包工具
注意: 打包整形数据时，如果确定整数大小则尽量使用具体的PacketAddInt8，PacketAddInt16，PacketAddInt32，不知道具体大小再使用PacketAddInt
*/

import {ARRAYBUFFER_UTILS, STRING_ARRAYBUFFER} from 'handlebytes.js'
import {execServerCommand} from 'servercommand.js'

let PROTOCOL_CB
if (typeof(PROTOCOL_CB) == "undefined"){
  PROTOCOL_CB = {}
}

function removeProtocolCB(iProtocol){
  if (iProtocol in PROTOCOL_CB){
    let cbFunc = PROTOCOL_CB[iProtocol]
    let state = -1 //表示超时
    cbFunc(state, null)
    delete PROTOCOL_CB[iProtocol]
  }
}

export function netCommand(header, oNetPack){
  if (! (header in PROTOCOL_CB)){
    execServerCommand(header, oNetPack)
    return
  }
  let cbFunc = PROTOCOL_CB[header]
  delete PROTOCOL_CB[header]
  try{
    let state = 1 //表示回调成功
    cbFunc(state, oNetPack)
  } catch(err){
    console.error(err)
  }
}

class CNetPackage{
  constructor(arraybuffer){
    this.m_Offset = 0
    this.m_DataList = []
    this.m_ArrayBuffer = arraybuffer
    this.m_DataView = null
  }

  PackInto(sType, data){
    this.m_DataList.push(data)
  }

  PackAll(){
    let tmpBuffer = ARRAYBUFFER_UTILS.concact(this.m_DataList)
    this.m_ArrayBuffer = tmpBuffer
  }

  UnpackPrepare(){
    this.m_DataView = new DataView(this.m_ArrayBuffer)
  }

  Unpack(sType, iStrLen = 0){
    switch (sType){
      case "B":
        let data1 = this.m_DataView.getUint8(this.m_Offset, true)
        this.m_Offset += 1
        return data1
      case "H":
        let data2 = this.m_DataView.getUint16(this.m_Offset, true)
        this.m_Offset += 2
        return data2
      case "I":
        let data3 = this.m_DataView.getUint32(this.m_Offset, true)
        this.m_Offset += 4
        return data3
      case "S":
        let data4 = this.UnpackS(iStrLen)
        this.m_Offset += iStrLen
        return data4
    }
  }

  UnpackS(iStrLen){
    return STRING_ARRAYBUFFER.dataview2string(this.m_DataView, this.m_Offset, iStrLen)
  }
}

export const NetPack = {
  PacketPrepare: function PacketPrepare (header, cbFunc=null) {
    if (cbFunc){
      PROTOCOL_CB[header] = cbFunc
    }
    setTimeout(removeProtocolCB, 10000, header)
    let oNetPack = new CNetPackage(null)
    this.PacketAddInt16(header, oNetPack)
    return oNetPack
  },

  PacketAddInt: function PacketAddInt(iVal, oNetPack){
    if (iVal <= 255){
      this.PacketAddInt8(1, oNetPack)
      this.PacketAddInt8(iVal, oNetPack)
    }
    else if (iVal > 255 && iVal <= 65535 ) {
      this.PacketAddInt8(2, oNetPack)
      this.PacketAddInt16(iVal, oNetPack)
    }
    else if (iVal > 65535 && iVal <= 4294967295 ) {
      this.PacketAddInt8(4, oNetPack)
      this.PacketAddInt32(iVal, oNetPack)
    }
    else{
      throw new Error("val pack exceeded", iVal)
    }
  },

  PacketAddInt8: function PacketAddInt8(iVal, oNetPack){
    let uint8array = new Uint8Array(1)
    uint8array[0] = iVal
    oNetPack.PackInto("B", uint8array.buffer)
  },

  PacketAddInt16: function PacketAddInt16(iVal, oNetPack){
    let uint16array = new Uint16Array(1)
    uint16array[0] = iVal
    oNetPack.PackInto("H", uint16array.buffer)
  },

  PacketAddInt32: function PacketAddInt32(iVal, oNetPack){
    let uint32array = new Uint32Array(1)
    uint32array[0] = iVal
    oNetPack.PackInto("I", uint32array.buffer)
  },

  PacketAddBool: function PacketAddBool(bVal, oNetPack){
    let iVal = 0
    if (bVal == true){
      iVal = 1
    }
    this.PacketAddInt8(iVal, oNetPack)
  },

  PacketAddS: function PacketAddS(str, oNetPack){
    let arraybuffer = STRING_ARRAYBUFFER.string2arraybuffer(str)
    let iStrLen = arraybuffer.byteLength
    this.PacketAddInt(iStrLen, oNetPack)
    oNetPack.PackInto("S", arraybuffer)
  },

  PacketSend: function PacketSend(oNetPack){
    let app = getApp()
    oNetPack.PackAll()
    if (!app.getConnectState()) {
      console.log("[error] disconnect with server, send data failed")
      return
    }
    let conn = app.getTcpConnect()
    conn.write(oNetPack.m_ArrayBuffer)
  },

  UnpackPrepare: function UnpackPrepare(arraybuffer){
    let oNetPack = new CNetPackage(arraybuffer)
    oNetPack.UnpackPrepare()
    return oNetPack
  },

  UnpackInt: function UnpackInt(oNetPack){
    let iByte = this.UnpackInt8(oNetPack)
    if (iByte == 1){
      return this.UnpackInt8(oNetPack)
    }
    else if (iByte == 2){
      return this.UnpackInt16(oNetPack)
    }
    else if (iByte == 4){
      return this.UnpackInt32(oNetPack)
    }
    else{
      throw new Error("netpackage error: UnpackInt bigger than int32")
    }
  },

  UnpackInt8: function UnpackInt8(oNetPack){
    return oNetPack.Unpack("B")
  },

  UnpackInt16: function UnpackInt16(oNetPack){
    return oNetPack.Unpack("H")
  },

  UnpackInt32: function UnpackInt32(oNetPack){
    return oNetPack.Unpack("I")
  },

  UnpackBool: function UnpackBool(oNetPack){
    let iVal = this.UnpackInt8(oNetPack)
    let bVal = false
    if (iVal == 1){
      bVal = true
    }
    return bVal
  },

  UnpackS: function UnpackS(oNetPack){
    let iLen = this.UnpackInt(oNetPack)
    return oNetPack.Unpack("S", iLen)
  }
}