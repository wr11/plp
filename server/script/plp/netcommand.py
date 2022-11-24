from protocol import CS_GETPZ, C2S_SENDPLP
from pubdefines import GetPlayerProxy
import netpackage as np
import script.plp.operatemanager as operatemanager

"""
C2S_SENDPLP 0x1010 发送plp
json        plp数据

CS_GETPZ 0x1009
"""

def Test(who, oNetPack, iDataHeader):
    i = np.UnpackInt8(oNetPack)
    s = np.UnpackS(oNetPack)
    PrintDebug("test i:%s s: %s"%(i, s))

    d = {"content": "wo henkaixin", "password":"mytoolffff"}
    oNetPack = np.PacketPrepare(CS_GETPZ)
    np.PacketAddInt8(len(d), oNetPack)
    for key,val in d.items():
        np.PacketAddS(key, oNetPack)
        np.PacketAddS(val, oNetPack)
    np.PacketSend(who.m_OpenID, oNetPack)

def NetCommand(who, oNetPack, iDataHeader):
    if iDataHeader == C2S_SENDPLP:
        dData = np.UnpackJSON(oNetPack)
        operatemanager.GetOperationManager().PublishPlp(who, dData)
    elif iDataHeader == CS_GETPZ:
        operatemanager.GetOperationManager().GetFivePlp(GetPlayerProxy(who.m_OpenID))
