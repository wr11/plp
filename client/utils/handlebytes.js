const BOOL_TYPE = 0,       // Bool
    INT8_TYPE = 1,       // Char
    UINT8_TYPE = 2,      // UChar
    INT16_TYPE = 3,      // Short
    UINT16_TYPE = 4,     // UShort
    INT32_TYPE = 5,      // Int
    INT64_TYPE = 6       // Long
    UINT32_TYPE = 7,     // UInt
    FLOAT32_TYPE = 8,    // Float
    FLOAT64_TYPE = 9,    // Double
    BYTE_TYPE = 10,      // Byte
    Str_TYPE = 11;  
    
// type：数据类型， Bin：二进制流，begin：数据起始位置（字节），Num: 1
function TypedArrays(Type, Bin) {//, begin, Num
    //var _num = 1;
    switch (Type) {
        case BOOL_TYPE: return Bin[0] == 1 ? true : false;
        case INT8_TYPE: return toInt8(Bin); 
        case UINT8_TYPE: return toUint8(Bin); 
        case INT16_TYPE: return toInt16(Bin);    
        case UINT16_TYPE: return toUint16(Bin);  
        case INT32_TYPE: return toInt32(Bin);    
        case INT64_TYPE: return toInt64(Bin);    
        case UINT32_TYPE: return toUint32(Bin);  
        case FLOAT32_TYPE: return toFloat32(Bin);
        case FLOAT64_TYPE: return toFloat64(Bin);
        case BYTE_TYPE: return toBytes(Bin);
        case Str_TYPE: return toString(Bin);
        default: return -1;
    }
}

// 截取指定大小数据并转换成指定的数据类型
function ByteToType(Type, Bin, begin, Num) {
    return TypedArrays(Type, Bin.splice(begin, Num));//, begin, Num);
}

// ASCII to char
function ASCII2Char(v) { return String.fromCharCode(v); }

// ASCII to string
function ASCII2Str(Bin, StartByte, Type, MsgLen) {
    var MsgName = "";
    var Index = 0;

    while (Index < MsgLen) {
        var AsciiValue = TypedArrays(Type, Bin, StartByte, 1); StartByte += 1;
        if (AsciiValue != 0)
            MsgName += ASCII2Char(AsciiValue);
        else
            return MsgName;
        Index++;
    }
    return MsgName;
}
function byteToString(arr) {
    if (typeof arr === 'string') {
        return arr;
    }
    var str = '',
        _arr = arr;
    for (var i = 0; i < _arr.length; i++) {
        var one = _arr[i].toString(2),
            v = one.match(/^1+?(?=0)/);
        if (v && one.length == 8) {
            var bytesLength = v[0].length;
            var store = _arr[i].toString(2).slice(7 - bytesLength);
            for (var st = 1; st < bytesLength; st++) {
                if (_arr.length > i + st) {
                    store += _arr[st + i].toString(2).slice(2);
                } else {
                    store = '000000';
                }
            }
            str += String.fromCharCode(parseInt(store, 2));
            i += bytesLength - 1;
        } else {
            str += String.fromCharCode(_arr[i]);
        }
    }
    return str;
}
           
//构建一个视图，把字节数组写到缓存中，索引从0开始，大端字节序
function getView(bytes) {
    var view = new DataView(new ArrayBuffer(bytes.length));
    for (var i = 0; i < bytes.length; i++) {
        view.setUint8(i, bytes[i]);
    }
    return view;
}

function toString(bytes) {
    //var data = getView(bytes);
    return byteToString(bytes);
}

//对应数组，或单数结果
function toBytes(bytes) {
    if (bytes.length > 1) {
        return bytes;
    } else {
        return bytes[0];
    }
}
//将字节数组转成有符号的8位整型，大端字节序
function toInt8(bytes) {
    return getView(bytes).getInt8();
}
//将字节数组转成无符号的8位整型，大端字节序
function toUint8(bytes) {
    return getView(bytes).getUint8();
}
//将字节数组转成有符号的16位整型，大端字节序
function toInt16(bytes) {
    return new Int16Array(getView(bytes).buffer, 0, 1)[0]; 
}
//将字节数组转成无符号的16位整型，大端字节序
function toUint16(bytes) {
    return new Uint16Array(getView(bytes).buffer, 0, 1)[0];
}
//将字节数组转成有符号的32位整型，大端字节序
function toInt32(bytes) {
    return new Int32Array(getView(bytes).buffer, 0, 1)[0]; 
}
//将字节数组转成无符号的32位整型，大端字节序
function toUint32(bytes) {
    return new Uint32Array(getView(bytes).buffer, 0, 1)[0]; 
}
//将字节数组转成有符号的64位整型，大端字节序
function toInt64(bytes) {
    return new BigInt64Array(getView(bytes).buffer, 0, 1)[0];
}
//将字节数组转成有符号的64位整型，大端字节序
function toUint64(bytes) {
    return new BigUint64Array(getView(bytes).buffer, 0, 1)[0];
}
//将字节数组转成32位浮点型，大端字节序
function toFloat32(bytes) {
    return getView(bytes).getFloat32();
}
//将字节数组转成64位浮点型，大端字节序
function toFloat64(bytes) {
    return new Float64Array(getView(bytes).buffer, 0, 1)[0]; 
}
//将数值写入到视图中，获得其字节数组，大端字节序
function getUint8Array(len, setNum) {
    var buffer = new ArrayBuffer(len);  //指定字节长度
    setNum(new DataView(buffer));  //根据不同的类型调用不同的函数来写入数值
    return new Uint8Array(buffer); //创建一个字节数组，从缓存中拿取数据
}
//得到一个8位有符号整型的字节数组，大端字节序
function getInt8Bytes(num) {
    return getUint8Array(1, function (view) { view.setInt8(0, num); })
}
//得到一个8位无符号整型的字节数组，大端字节序
function getUint8Bytes(num) {
    return getUint8Array(1, function (view) { view.setUint8(0, num); })
}
//得到一个16位有符号整型的字节数组，大端字节序
function getInt16Bytes(num) {
    return getUint8Array(2, function (view) { view.setInt16(0, num); })
}
//得到一个16位无符号整型的字节数组，大端字节序
function getUint16Bytes(num) {
    return getUint8Array(2, function (view) { view.setUint16(0, num); })
}
//得到一个32位有符号整型的字节数组，大端字节序
function getInt32Bytes(num) {
    return getUint8Array(4, function (view) { view.setInt32(0, num); })
}
//得到一个32位无符号整型的字节数组，大端字节序
function getUint32Bytes(num) {
    return getUint8Array(4, function (view) { view.setUint32(0, num); })
}
//得到一个32位浮点型的字节数组，大端字节序
function getFloat32Bytes(num) {
    return getUint8Array(4, function (view) { view.setFloat32(0, num); })
}
//得到一个64位浮点型的字节数组，大端字节序
function getFloat64Bytes(num) {
    return getUint8Array(8, function (view) { view.setFloat64(0, num); })
}

export const STRING_ARRAYBUFFER = {
    string2arraybuffer : function stringToArrayBuffer(str) {
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