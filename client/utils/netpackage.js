/*

*/

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
        d
    }
}