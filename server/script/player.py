# -*- coding: utf-8 -*-

from myutil.mycorotine import coroutine, Return
from timer import Call_out, GetTimer, Remove_Call_out
from gc import collect
from pubdefines import GetPlayerProxy, IsProxyExist
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
		if not oPlayer.m_Loaded:
			continue
		try:
			playerdata = oPlayer.Save()
			data[oPlayer.m_OpenID] = playerdata
		except:
			continue
	iServer, iIndex = conf.GetDBS()
	rpc.RemoteCallFunc(iServer, iIndex, None, "datahub.manager.UpdatePlayerShadowData", data)
	if not lstPlayer:
		return
	Call_out(2, "truesaveplayer", TrueSavePlayer, lstPlayer)

@coroutine
def SaveOnePlayer(oPlayer_proxy):
	if getattr(oPlayer_proxy, "m_Login", 0):
		PrintWarning("player is in login, after 10s will offline again")
		raise Return(0)
	bFinish = False
	try:
		data = {}
		playerdata = oPlayer_proxy.Save()
		data[oPlayer_proxy.m_OpenID] = playerdata
		bFinish = True
	except Exception as e:
		PrintError(oPlayer_proxy, e)
		bFinish = False
	if bFinish:
		iServer, iIndex = conf.GetDBS()
		ret = yield rpc.AsyncRemoteCallFunc(iServer, iIndex, "datahub.manager.UpdatePlayerShadowData", data)
		raise Return(ret)
	else:
		raise Return(0)

class CPlayer:
	def __init__(self, sOpenID, iConnectID):
		self.m_OpenID = sOpenID
		self.m_ConnectID = iConnectID
		self.m_Loaded = False
		self.m_SaveState = {
			"m_SendedNum": False,
			"m_SendedList": False,
		}

		#需要存盘的数据
		self.m_SendedNum = 0
		self.m_SendedList = []

	def __repr__(self):
		return "<player(%s) %s %s>" % (self.m_ConnectID, self.m_OpenID, str(self.m_SaveState))

	def GetConnectID(self):
		return self.m_ConnectID

	def SetSaveState(self, sAttr, bState):
		self.m_SaveState[sAttr] = bState

	def GetAttrNeedSave(self, sAttr):
		return self.m_SaveState[sAttr]

	def GetSaveAttrList(self):
		return self.m_SaveState.keys()

	def Save(self):
		data = {}
		lstAttr = self.GetSaveAttrList()
		if not lstAttr:
			return data
		for sAttr in lstAttr:
			if self.GetAttrNeedSave(sAttr):
				self.SetSaveState(sAttr, False)
				data[sAttr] = getattr(self, sAttr, None)
		return data

	def Load(self, data):
		if not data:
			return
		for sAttr, val in data.items():
			setattr(self, sAttr, val)

	def AddhPlp(self, iNum, sID):
		self.m_SendedNum += iNum
		if sID not in self.m_SendedList:
			PrintWarning("%s plpid repeated"%self.m_OpenID)
			self.m_SendedList.append(sID)
		self.SetSaveState("m_SendedNum", True)
		self.SetSaveState("m_SendedList", True)

	def CheckPulishCnt(self, iNum):
		return True

def MakePlayer(sOpenID, iConnectID):
	oPlayer = CPlayer(sOpenID, iConnectID)
	bRet = AddPlayer(sOpenID, iConnectID, oPlayer)
	return 10 + bRet

def AddPlayer(sOpenID, iConnectID, oPlayer):
	global PLAYER_LIST, CONNECTID2OPENID
	if sOpenID in PLAYER_LIST and iConnectID not in CONNECTID2OPENID:
		who = PLAYER_LIST[sOpenID]
		if getattr(who, "m_OffLine", 0):
			return 3
		else:
			return 4
	if sOpenID in PLAYER_LIST and iConnectID in CONNECTID2OPENID:
		return 5
	PLAYER_LIST[sOpenID] = oPlayer
	CONNECTID2OPENID[iConnectID] = sOpenID
	return 0

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
	who_proxy = GetPlayerProxy(sOpenID)
	if not who_proxy:
		PrintWarning("%s player object has already unloaded"%sOpenID)
		return
	if getattr(who_proxy, "m_OffLine", 0):
		PrintWarning("%s player is in offline"%sOpenID)
		return
	who_proxy.m_OffLine = 1
	ret = yield SaveOnePlayer(who_proxy)
	if ret:
		iServer, iIndex = conf.GetDBS()
		rpc.RemoteCallFunc(iServer, iIndex, None, "datahub.datashadow.RemovePlayerDataShadow", sOpenID)
		RemovePlayer(sOpenID, iConnectID)
	else:
		PrintWarning("player%s offline save failed!!!!!"%sOpenID)

		Call_out(10, "reoffline", PlayerOffLine, None, iConnectID)
