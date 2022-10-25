/*

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
        let data4 = this.UnpackString(iStrLen)
        this.m_Offset += iStrLen
        return data4
    }
  }

  UnpackString(iStrLen){
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
    this.PacketAddI(header, oNetPack)
    return oNetPack
  },

  PacketAddI: function PacketAddI(iVal, oNetPack){
    if (iVal <= 255){
      let uint8array = new Uint8Array(1)
      uint8array[0] = iVal
      oNetPack.PackInto("B", uint8array.buffer)
    }
    else if (iVal > 255 && iVal <= 65535 ) {
      let uint16array = new Uint16Array(1)
      uint16array[0] = iVal
      oNetPack.PackInto("H", uint16array.buffer)
    }
    else if (iVal > 65535 && iVal <= 4294967295 ) {
      let uint32array = new Uint32Array(1)
      uint32array[0] = iVal
      oNetPack.PackInto("I", uint32array.buffer)
    }
    else{
      throw new Error("val pack exceeded", iVal)
    }
  },

  PacketAddBool: function PacketAddBool(bVal, oNetPack){
    iVal = 0
    if (bVal == true){
      iVal = 1
    }
    this.PacketAddI(iVal, oNetPack)
  },

  PacketAddS: function PacketAddS(str, oNetPack){
    let arraybuffer = STRING_ARRAYBUFFER.string2arraybuffer(str)
    let iStrLen = arraybuffer.byteLength
    if (iStrLen <= 255){
      this.PacketAddI(1, oNetPack)
    }
    else if (255 < iStrLen <= 65535){
      this.PacketAddI(2, oNetPack)
    }
    else if (65535 < iStrLen <= 4294967295){
      this.PacketAddI(4, oNetPack)
    }
    else{
      this.PacketAddI(4, oNetPack)
      console.log("netpack: string len exceeded!")
    }
    this.PacketAddI(iStrLen, oNetPack)
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
    iVal = this.UnpackInt8(oNetPack)
    bVal = false
    if (iVal == 1){
      bVal = true
    }
    return bVal
  },

  UnpackString: function UnpackString(oNetPack){
    let iBt = this.UnpackInt8(oNetPack)
    let iLen = 0
    if (iBt == 1){
      iLen = this.UnpackInt8(oNetPack)
    }
    else if (iBt == 2){
      iLen = this.UnpackInt16(oNetPack)
    }
    else if (iBt == 4){
      iLen = this.UnpackInt32(oNetPack)
    }
    else{
      iLen = this.UnpackInt32(oNetPack)
      console.log("netpack: string len exceeded!")
    }

    return oNetPack.Unpack("S", iLen)
  }
}