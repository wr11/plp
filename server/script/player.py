# -*- coding: utf-8 -*-

from myutil.mycorotine import coroutine, Return
from timer import Call_out
from gc import collect
import rpc,conf

if "PLAYER_LIST" not in globals():
	PLAYER_LIST = {}

if "CONNECTID2OPENID" not in globals():
	CONNECTID2OPENID = {}

def Init():
	Call_out(5*60, "saveplayer", SavePlayers)

def SavePlayers():
	global PLAYER_LIST
	if not PLAYER_LIST:
		return
	lstRoleList = PLAYER_LIST.values()
	Call_out(2, "truesaveplayer", TrueSavePlayer, lstRoleList)

def TrueSavePlayer(lstPlayer):
	data = {}
	lstTemp = lstPlayer[0:50]
	del lstPlayer[0:50]
	for oPlayer in lstTemp:
		playerdata = oPlayer.Save()
		data[oPlayer.m_OpenID] = playerdata
	iServer, iIndex = conf.GetDBS()
	rpc.RemoteCallFunc(iServer, iIndex, None, "datahub.manager.UpdatePlayerShadowData", data)
	if not lstPlayer:
		return
	Call_out(2, "truesaveplayer", TrueSavePlayer, lstPlayer)

@coroutine
def SaveOnePlayer(oPlayer):
	data = {}
	playerdata = oPlayer.Save()
	data[oPlayer.m_OpenID] = playerdata
	iServer, iIndex = conf.GetDBS()
	ret = yield rpc.RemoteCallFunc(iServer, iIndex, None, "datahub.manager.UpdatePlayerShadowData", data)
	raise Return(ret)

class CPlayer:
	def __init__(self, sOpenID, iConnectID):
		self.m_OpenID = sOpenID
		self.m_ConnectID = iConnectID
		self.m_SaveState = {
			"m_SendedNum": False,
			"m_SendedList": False,
		}

		#需要存盘的数据
		self.m_SendedNum = 0
		self.m_SendedList = []

	def GetConnectID(self):
		return self.m_ConnectID

	def SetSaveState(self, sAttr, bState):
		self.m_SaveState[sAttr] = bState

	def GetAttrNeedSave(self, sAttr):
		return self.m_SaveState[sAttr]

	def IncreaseSend(self, iNum, sID):
		self.m_SendedNum += iNum
		if sID in self.m_SendedList:
			self.m_SendedList.append(sID)
		self.SetSaveState("m_SendedNum", True)
		self.SetSaveState("m_SendedList", True)


	def Save(self):
		data = {}
		if self.GetAttrNeedSave("m_SendedNum"):
			data["m_SendedNum"] = self.m_SendedNum
			self.SetSaveState("m_SendedNum", False)
		if self.GetAttrNeedSave("m_SendedList"):
			data["m_SendedList"] = self.m_SendedList
			self.SetSaveState("m_SendedNum", False)
		return data

	def Load(self, data):
		if not data:
			return
		for sAttr, val in data.items():
			setattr(self, sAttr, val)

def MakePlayer(sOpenID, iConnectID):
	return CPlayer(sOpenID, iConnectID)

def AddPlayer(sOpenID, iConnectID, oPlayer):
	global PLAYER_LIST, CONNECTID2OPENID
	if sOpenID in PLAYER_LIST and iConnectID not in CONNECTID2OPENID:
		PrintError("player data is in reset danger!!")
		return
	PLAYER_LIST[sOpenID] = oPlayer
	CONNECTID2OPENID[iConnectID] = sOpenID

def RemovePlayer(sOpenID, iConnectID):
	global PLAYER_LIST, CONNECTID2OPENID
	del PLAYER_LIST[sOpenID]
	del CONNECTID2OPENID[iConnectID]

def GetOnlinePlayer(sOpenID):
	global PLAYER_LIST
	return PLAYER_LIST.get(sOpenID, None)

def GetOnlinePlayerNum():
	global PLAYER_LIST
	return len(PLAYER_LIST)

def GetConnectIDByOpenID(sOpenID):
	global PLAYER_LIST
	oPlayer = PLAYER_LIST.get(sOpenID, None)
	if not oPlayer or (hasattr(oPlayer, "m_OffLine")):
		PrintError("%s has no player object"%sOpenID)
		return -1
	return oPlayer.GetConnectID()

def GetOpenIDByConnectID(iConnectID):
	global CONNECTID2OPENID
	return CONNECTID2OPENID.get(iConnectID, "")

@coroutine
def PlayerOffLine(response, iConnectID):
	sOpenID = GetOpenIDByConnectID(iConnectID)
	who = GetOnlinePlayer(sOpenID)
	RemovePlayer(sOpenID, iConnectID)
	who.m_OffLine = 1
	return
	ret = yield SaveOnePlayer(who)
	if ret:
		del who

		iServer, iIndex = conf.GetDBS()
		rpc.RemoteCallFunc(iServer, iIndex, None, "datahub.datashadow.RemovePlayerDataShadow", sOpenID)
		response(1)
	else:
		PrintWarning("player%s offline save failed!!!!!"%sOpenID)

		Call_out(5*60, "reoffline", PlayerOffLine, None, iConnectID)
