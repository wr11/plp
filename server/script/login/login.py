# -*- coding: utf-8 -*-

from protocol import CS_LOGIN
from myutil.mycorotine import coroutine, Return

import netpackage as np
import script.player as player

@coroutine
def Login(iConnectID, oNetPackage):
	sOpenID = np.UnpackS(oNetPackage)
	del oNetPackage
	who = player.MakePlayer(sOpenID, iConnectID)
	player.AddPlayer(sOpenID, iConnectID, who)
	iRet = yield CheckRole(sOpenID)
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
	iRet = yield rpc.AsyncRemoteCallFunc(iServer, iIndex, "datahub.manager.LoadPlayerDataShadow", sOpenID)
	raise Return(iRet)

def S2CLoginFailed(sOpenID, iRet):
	oNetPack = np.PacketPrepare(CS_LOGIN)
	np.PacketAddI(iRet, oNetPack)
	np.PacketSend(sOpenID, oNetPack)

def S2CLoginSuccess(sOpenID):
	oNetPack = np.PacketPrepare(CS_LOGIN)
	np.PacketAddI(1, oNetPack)
	np.PacketSend(sOpenID, oNetPack)