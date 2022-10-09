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
        this.m_ArrayBuffer = null
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
        this.m_ArrayBuffer = new ArrayBuffer(iSumLen)
        var oDataView = new DataView(this.m_ArrayBuffer)
        var iLen = this.m_TypeList.length
        var iOffset = 0
        for (i=0; i < iLen; i++){
            sTypeName = this.m_TypeList[i]
            switch (sTypeName) {
                case "B" : oDataView.setUint8(iOffset, this.m_DataList[i])
                case "H" : oDataView.setUint16(iOffset, this.m_DataList[i])
                case "I" : oDataView.setUint32(iOffset, this.m_DataList[i])
            }
            iOffset = iOffset + TYPE_NAME2TYPE_ARRY_LEN[sTypeName]
        }
    }
}