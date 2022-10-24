# -*- coding: utf-8 -*-

from protocol import CS_LOGIN
from myutil.mycorotine import coroutine, Return
from pubdefines import GetPlayerProxy

import netpackage as np
import script.player as player

@coroutine
def Login(iConnectID, oNetPackage):
	sOpenID = np.UnpackS(oNetPackage)
	del oNetPackage
	player.MakePlayer(sOpenID, iConnectID)
	iRet = yield CheckRole(sOpenID)		#1为成功，10以上为失败码
	if iRet > 10:
		S2CLoginFailed(sOpenID, iRet)
		player.RemovePlayer(sOpenID, iConnectID)
		return
	PrintNotify("%s login success"%sOpenID)
	S2CLoginSuccess(sOpenID)

@coroutine
def CheckRole(sOpenID):
	import rpc
	import conf
	iServer, iIndex = conf.GetDBS()
	ret = yield rpc.AsyncRemoteCallFunc(iServer, iIndex, "datahub.manager.LoadPlayerDataShadow", sOpenID)
	iCode, data = ret
	iCode = int(iCode)
	if data and iCode == 1:
		player.GetOnlinePlayer(sOpenID).Load(data)
		player.GetOnlinePlayer(sOpenID).m_Loaded = True
	raise Return(iCode)

def S2CLoginFailed(sOpenID, iRet):
	oNetPack = np.PacketPrepare(CS_LOGIN)
	np.PacketAddI(iRet, oNetPack)
	np.PacketSend(sOpenID, oNetPack)

def S2CLoginSuccess(sOpenID):
	oNetPack = np.PacketPrepare(CS_LOGIN)
	np.PacketAddI(1, oNetPack)
	np.PacketSend(sOpenID, oNetPack)