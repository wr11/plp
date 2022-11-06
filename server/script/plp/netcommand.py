from protocol import CS_GETPZ
import netpackage as np

def Test(who, oNetPack):
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