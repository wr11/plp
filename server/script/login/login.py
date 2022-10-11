# -*- coding: utf-8 -*-

from protocol import CS_LOGIN

import netpackage as np
import script.player as player

def Login(iConnectID, oNetPackage):
	sOpenID = np.UnpackS(oNetPackage)
	del oNetPackage
	who = player.MakePlayer(sOpenID, iConnectID)
	player.AddPlayer(sOpenID, iConnectID, who)
	iRet = CheckRole(sOpenID)
	if iRet > 10:
		S2CLoginFailed(sOpenID, iRet)
		player.RemovePlayer(sOpenID, iConnectID)
		return
	PrintNotify("%s login success"%sOpenID)
	S2CLoginSuccess(sOpenID)

def CheckRole(sOpenID):
	return 1

def S2CLoginFailed(sOpenID, iRet):
	oNetPack = np.PacketPrepare(CS_LOGIN)
	np.PacketAddI(iRet, oNetPack)
	np.PacketSend(sOpenID, oNetPack)

def S2CLoginSuccess(sOpenID):
	oNetPack = np.PacketPrepare(CS_LOGIN)
	np.PacketAddI(1, oNetPack)
	np.PacketSend(sOpenID, oNetPack)