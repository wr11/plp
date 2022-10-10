export const STRING_ARRAYBUFFER = {
  string2arraybuffer : function stringToArrayBuffer(str) {
        let bytes = new Array(); 
        let len,c;
        len = str.length;
        for(let i = 0; i < len; i++){
            c = str.charCodeAt(i);
            if(c >= 0x010000 && c <= 0x10FFFF){
                bytes.push(((c >> 18) & 0x07) | 0xF0);
                bytes.push(((c >> 12) & 0x3F) | 0x80);
                bytes.push(((c >> 6) & 0x3F) | 0x80);
                bytes.push((c & 0x3F) | 0x80);
            }else if(c >= 0x000800 && c <= 0x00FFFF){
                bytes.push(((c >> 12) & 0x0F) | 0xE0);
                bytes.push(((c >> 6) & 0x3F) | 0x80);
                bytes.push((c & 0x3F) | 0x80);
            }else if(c >= 0x000080 && c <= 0x0007FF){
                bytes.push(((c >> 6) & 0x1F) | 0xC0);
                bytes.push((c & 0x3F) | 0x80);
            }else{
                bytes.push(c & 0xFF);
            }
        }
        let array = new Int8Array(bytes.length);
        for(let i in bytes){
            array[i] =bytes[i];
        }
        return array.buffer;
    },

  arraybufferview2string : function arraybufferview2string(arraybufferview){
    let arr=arraybufferview;
    let str = '',
    _arr = arr;
    for(let i = 0; i < _arr.length; i++) {
      let one = _arr[i].toString(2),
      v = one.match(/^1+?(?=0)/);
      if(v && one.length == 8) {
        let bytesLength = v[0].length;
        let store = _arr[i].toString(2).slice(7 - bytesLength);
        for(let st = 1; st < bytesLength; st++) {
          store += _arr[st + i].toString(2).slice(2);
        }
        str += String.fromCharCode(parseInt(store, 2));
        i += bytesLength - 1;
      } else {
        str += String.fromCharCode(_arr[i]);
      }
    }
    return str;
  },

  dataview2string : function dataview2string(dataview, iOffset, iLen){
    let arraybuffer = new ArrayBuffer(iLen)
    let newview = new Uint8Array(arraybuffer)
    let iIndex = iOffset
    for (let i = iOffset; i < iLen + iOffset; i++){
      let data = dataview.getUint8(iIndex)
      newview[i - iOffset] = data
      iIndex += 1
    }

    return this.arraybufferview2string(newview)
  }
}

export const ARRAYBUFFER_UTILS = {
  concact : function concact (arraybuffers){
    let iTotalLen = 0
    for (let arraybuffer of arraybuffers){
      iTotalLen += arraybuffer.byteLength
    }
    let result = new Uint8Array(iTotalLen)
    let offset = 0
    for (let arraybuffer1 of arraybuffers) {
      let uint8Arr = new Uint8Array(arraybuffer1)
      result.set(uint8Arr, offset)
      offset += arraybuffer1.byteLength
    }
    return result.buffer
  },

  extend: function extend(to_arraybuffer, from_arraybuffer, iOffset){
    if (iOffset + from_arraybuffer.byteLength > to_arraybuffer.byteLength){
      throw new Error("arraybuffer extend exceeded!")
    }
    let to_view = new Uint8Array(to_arraybuffer)
    let from_view = new Uint8Array(from_arraybuffer)
    to_view.set(from_view, iOffset)
    return to_view.buffer
  },

  extendbydataview: function extendbydataview(to_view, from_view, iOffset){
    if (iOffset + from_view.byteLength > to_view.byteLength){
      throw new Error("arraybuffer extend exceeded!")
    }
    to_view.set(from_view, iOffset)
    return to_view
  },
}