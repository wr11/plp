# -*- coding: utf-8 -*-

from protocol import CS_LOGIN
from myutil.mycorotine import coroutine, Return
from pubdefines import GetPlayerProxy, IsProxyExist

import netpackage as np
import script.player as player

@coroutine
def Login(iConnectID, oNetPackage):
	sOpenID = np.UnpackS(oNetPackage)
	iRet = player.MakePlayer(sOpenID, iConnectID)
	if iRet > 10:
		S2CLoginFailed(iConnectID, iRet)
		return
	oPlayer_proxy = GetPlayerProxy(sOpenID, False)
	oPlayer_proxy.m_Login = 1
	iRet = yield CheckRole(sOpenID)		#10为成功，10以上为失败码
	if iRet > 10:
		S2CLoginFailed(iConnectID, iRet)
		if IsProxyExist(oPlayer_proxy):
			oPlayer_proxy.m_Login = 0
		player.RemovePlayer(sOpenID, iConnectID)
		return
	PrintNotify("%s login success"%sOpenID)
	if IsProxyExist(oPlayer_proxy):
		oPlayer_proxy.m_Login = 0
	S2CLoginSuccess(sOpenID)

@coroutine
def CheckRole(sOpenID):
	import rpc
	import conf
	iServer, iIndex = conf.GetDBS()
	ret = yield rpc.AsyncRemoteCallFunc(iServer, iIndex, "datahub.manager.LoadPlayerDataShadow", sOpenID)
	iCode, data = ret
	iCode = int(iCode)
	if data and iCode == 10:
		player.GetPlayer(sOpenID).Load(data)
		player.GetPlayer(sOpenID).m_Loaded = True
	raise Return(iCode)

def S2CLoginFailed(iConnectID, iRet):
	oNetPack = np.PacketPrepare(CS_LOGIN)
	np.PacketAddI(iRet, oNetPack)
	np.GPSPacketSendByConnectID(iConnectID, oNetPack)

def S2CLoginSuccess(sOpenID):
	oNetPack = np.PacketPrepare(CS_LOGIN)
	np.PacketAddI(1, oNetPack)
	np.PacketSend(sOpenID, oNetPack)