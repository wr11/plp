# -*- coding: utf-8 -*-

from protocol import CS_LOGIN
from myutil.mycorotine import coroutine, Return
from pubdefines import GetPlayerProxy, IsProxyExist
from script.gameinit import GetServerState

import netpackage as np
import script.player as player

@coroutine
def Login(iConnectID, sOpenID):
	from script.gm.defines import IsAuth
	iServerState = yield GetServerState()
	if iServerState == 0:
		S2CLoginFailed(iConnectID, 18)
		return
	elif iServerState == 1:
		if not IsAuth(sOpenID):
			S2CLoginFailed(iConnectID, 17)
			return
	iRet = player.MakePlayer(sOpenID, iConnectID)
	if iRet > 10:
		S2CLoginFailed(iConnectID, iRet)
		return
	oPlayer_proxy = GetPlayerProxy(sOpenID, False)
	oPlayer_proxy.m_Login = 1
	iRet = yield CheckRole(sOpenID, oPlayer_proxy)		#10为成功，10以上为失败码
	if iRet > 10:
		S2CLoginFailed(iConnectID, iRet)
		if IsProxyExist(oPlayer_proxy):
			oPlayer_proxy.m_Login = 0
		player.RemovePlayer(sOpenID, iConnectID)
		return
	PrintNotify("%s login success"%sOpenID)
	if IsProxyExist(oPlayer_proxy):
		oPlayer_proxy.m_Login = 0
	
	bAuth = False
	if IsAuth(sOpenID):
		bAuth = True
	S2CLoginSuccess(sOpenID, bAuth)

@coroutine
def CheckRole(sOpenID, oPlayer_proxy):
	import rpc
	import conf
	iServer, iIndex = conf.GetDBS()
	ret = yield rpc.AsyncRemoteCallFunc(iServer, iIndex, "datahub.manager.LoadPlayerDataShadow", sOpenID, oPlayer_proxy.GetSaveAttrList(bList = True))
	iCode, data = ret
	iCode = int(iCode)
	try:
		if data and iCode == 10:
			player.GetPlayer(sOpenID).Load(data)
			player.GetPlayer(sOpenID).m_Loaded = True
			player.GetPlayer(sOpenID).FillDefault()
			player.GetPlayer(sOpenID).AfterLoad()
	except Exception as e:
		PrintError(e)
		iCode = 16
	raise Return(iCode)

def S2CLoginFailed(iConnectID, iRet):
	oNetPack = np.PacketPrepare(CS_LOGIN)
	np.PacketAddInt8(iRet, oNetPack)
	np.GPSPacketSendByConnectID(iConnectID, oNetPack)

def S2CLoginSuccess(sOpenID, bAuth):
	oNetPack = np.PacketPrepare(CS_LOGIN)
	np.PacketAddInt8(1, oNetPack)
	np.PacketAddBool(bAuth, oNetPack)
	np.PacketSend(sOpenID, oNetPack)