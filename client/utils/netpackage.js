/*

*/

import {ARRAYBUFFER_UTILS, STRING_ARRAYBUFFER} from 'handlebytes.js'

const TYPE_NAME2TYPE_ARRY_LEN = {
    "B" : Uint8Array.BYTES_PER_ELEMENT,
    "H" : Uint16Array.BYTES_PER_ELEMENT,
    "I" : Uint32Array.BYTES_PER_ELEMENT
}

class CNetPackage{
  constructor(arraybuffer){
    this.m_Offset = 0
    this.m_DataList = []
    this.m_ArrayBuffer = arraybuffer
  }

  PackInto(sType, data){
    this.m_DataList.push(data)
  }

  PackAll(){
    let tmpBuffer = ARRAYBUFFER_UTILS.concact(this.m_DataList)
    this.m_ArrayBuffer = tmpBuffer
  }
}

export const NetPack = {
  PacketPrepare: function PacketPrepare (header) {
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
    if (!app.GetConnectState()) {
      console.log("[error] disconnect with server, send data failed")
      return
    }
    let conn = app.GetTcpConnect()
    conn.write(oNetPack.m_ArrayBuffer)
  }
}