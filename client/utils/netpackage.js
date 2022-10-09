/*

*/

import {ARRAYBUFFER_UTILS} from 'handlebytes.js'

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

export function PacketPrepare (header) {
  let oNetPack = new CNetPackage(null)
  PacketAddI(header, oNetPack)
  return oNetPack
}

export function PacketAddI(iVal, oNetPack){
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
}

export function PacketSend(oNetPack){
  let app = getApp()
  oNetPack.PackAll()
  if (!app.GetConnectState()) {
    console.log("[error] disconnect with server, send data failed")
    return
  }
  let conn = app.GetTcpConnect()
  conn.write(oNetPack.m_ArrayBuffer)
}