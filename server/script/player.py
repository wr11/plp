# -*- coding: utf-8 -*-

from myutil.mycorotine import coroutine, Return
from timer import Call_out, GetTimer, Remove_Call_out
from gc import collect
from pubdefines import GetPlayerProxy, IsProxyExist
import rpc,conf

INTERVAL_SAVEPLAYERS = 2

if "PLAYER_LIST" not in globals():
	PLAYER_LIST = {}

if "CONNECTID2OPENID" not in globals():
	CONNECTID2OPENID = {}

def Init():
	Call_out(INTERVAL_SAVEPLAYERS, "saveplayer", SavePlayers)

	PrintNotify("Player Inited")

def SavePlayers():
	global PLAYER_LIST
	if not PLAYER_LIST:
		Call_out(INTERVAL_SAVEPLAYERS, "saveplayer", SavePlayers)
		return
	lstRoleList = PLAYER_LIST.values()
	TrueSavePlayer(list(lstRoleList))

def TrueSavePlayer(lstPlayer):
	data = {}
	lstTemp = lstPlayer[0:50]
	del lstPlayer[0:50]
	for oPlayer in lstTemp:
		if not oPlayer.m_Loaded:
			continue
		try:
			playerdata = oPlayer.Save()
			if not playerdata:
				continue
			data[oPlayer.m_OpenID] = playerdata
		except:
			continue

	if data:
		iServer, iIndex = conf.GetDBS()
		rpc.RemoteCallFunc(iServer, iIndex, None, "datahub.manager.UpdatePlayerShadowData", data)
	if not lstPlayer:
		Call_out(INTERVAL_SAVEPLAYERS, "saveplayer", SavePlayers)
		return
	Call_out(5, "truesaveplayer", TrueSavePlayer, lstPlayer)

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
			"m_GetPlpWay": False,
			"m_SendedAllNum": False,
		}

		#需要存盘的数据
		self.m_SendedNum = 0
		self.m_SendedAllNum = 0
		self.m_SendedList = []
		self.m_GetPlpWay = 1		#1-不获取重复的 2-获取重复的

	def __repr__(self):
		return "<player(%s) %s %s>" % (self.m_ConnectID, self.m_OpenID, str(self.m_SaveState))

	def AfterLoad(self):
		if not self.m_SendedNum:
			self.m_SendedNum = 0
		if not self.m_SendedAllNum:
			self.m_SendedAllNum = 0
		if not self.m_SendedList:
			self.m_SendedList = []
		if not self.m_GetPlpWay:
			self.m_GetPlpWay = 1

	def GetSaveAttrList(self, bList = False):
		if not bList:
			return self.m_SaveState.keys()
		else:
			return list(self.m_SaveState.keys())

	def GetConnectID(self):
		return self.m_ConnectID

	def SetSaveState(self, sAttr, bState):
		self.m_SaveState[sAttr] = bState

	def GetAttrNeedSave(self, sAttr):
		return self.m_SaveState[sAttr]

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

	def ResetPlp(self):
		self.SetSaveState("m_SendedNum", True)
		self.SetSaveState("m_SendedList", True)
		self.SetSaveState("m_SendedAllNum", True)
		self.m_SendedNum = 0
		self.m_SendedList = []
		self.m_SendedAllNum = 0

	def AddPlp(self, iPlpID):
		if iPlpID in self.m_SendedList:
			PrintWarning("%s plpid repeated"%self.m_OpenID)
		else:
			self.m_SendedList.append(iPlpID)
			self.m_SendedNum += 1
			self.m_SendedAllNum += 1
			self.SetSaveState("m_SendedNum", True)
			self.SetSaveState("m_SendedList", True)
			self.SetSaveState("m_SendedAllNum", True)

	def RemovePlp(self, iPlpID):
		self.m_SendedNum -= 1
		if self.m_SendedNum < 0:
			self.m_SendedNum = 0
		if iPlpID in self.m_SendedList:
			self.m_SendedList.remove(iPlpID)
		self.SetSaveState("m_SendedNum", True)
		self.SetSaveState("m_SendedList", True)

	def CheckPulishCnt(self, iNum):
		return True

	def GetPlpWay(self):
		return self.m_GetPlpWay

	def SetPlpWay(self, iWay):
		self.SetSaveState("m_GetPlpWay", True)
		self.m_GetPlpWay = iWay

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
	oPlayer =  PLAYER_LIST.get(sOpenID, None)
	if oPlayer and oPlayer.m_Loaded:
		return oPlayer
	return None

def GetPlayer(sOpenID):
	global PLAYER_LIST
	oPlayer =  PLAYER_LIST.get(sOpenID, None)
	return oPlayer

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
	if not sOpenID:
		return
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
