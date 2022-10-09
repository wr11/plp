/*

*/

const TYPE_NAME2TYPE_ARRY_LEN = {
    "B" : Uint8Array.BYTES_PER_ELEMENT,
    "H" : Uint16Array.BYTES_PER_ELEMENT,
    "I" : Uint32Array.BYTES_PER_ELEMENT
}

class CNetPackage{
    constructor(bytes){
        this.m_BytesBuffer = bytes
        this.m_Offset = 0
        this.m_TypeList = new Array()
        this.m_DataList = new Array()
    }

    PackEachInto(sType, data){
        this.m_TypeList.push(sType)
        this.m_DataList.push(data)
    }

    PackAll(){
        var iSumLen = 0
        for (sType of  this.m_TypeList) {
            iSumLen = iSumLen + TYPE_NAME2TYPE_ARRY_LEN[sType]
        }
        var oArrayBuffer = new ArrayBuffer(iSumLen)
    }
}