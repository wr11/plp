export const STRING_ARRAYBUFFER = {
    addstring2arraybuffer : function stringToArrayBuffer(arrbuffer, offset, str) {
        var bytes = new Array(); 
        var len,c;
        len = str.length;
        for(var i = 0; i < len; i++){
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
        var array = new Int8Array(bytes.length);
        for(var i in bytes){
            array[i] =bytes[i];
        }
        return array.buffer;
    },

    arraybuffer2string : function arrayBufferToString(arr){
        if(typeof arr === 'string') {  
            return arr;  
        }  
        var dataview=new DataView(arr.data);
        var ints=new Uint8Array(arr.data.byteLength);
        for(var i=0;i<ints.length;i++){
        ints[i]=dataview.getUint8(i);
        }
        arr=ints;
        var str = '',  
            _arr = arr;  
        for(var i = 0; i < _arr.length; i++) {  
            var one = _arr[i].toString(2),  
                v = one.match(/^1+?(?=0)/);  
            if(v && one.length == 8) {  
                var bytesLength = v[0].length;  
                var store = _arr[i].toString(2).slice(7 - bytesLength);  
                for(var st = 1; st < bytesLength; st++) {  
                    store += _arr[st + i].toString(2).slice(2);  
                }  
                str += String.fromCharCode(parseInt(store, 2));  
                i += bytesLength - 1;  
            } else {  
                str += String.fromCharCode(_arr[i]);  
            }  
        }  
        return str; 
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