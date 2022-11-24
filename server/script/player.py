# -*- coding: utf-8 -*-

from myutil.mycorotine import coroutine, Return
from timer import Call_out, GetTimer, Remove_Call_out
from gc import collect
from pubdefines import GetPlayerProxy, IsProxyExist, GetNowTime, GetDay5Sec, GetDayNo, GetDay0Sec
from netpackage import PacketPrepare, PacketSend
from protocol import S2C_OFFLINE

import rpc,conf
import weakref

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
	if not getattr(oPlayer_proxy, "m_Loaded", 0):
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
		PrintDebug("SaveOnePlayer", data)
		iServer, iIndex = conf.GetDBS()
		ret = yield rpc.AsyncRemoteCallFunc(iServer, iIndex, "datahub.manager.UpdatePlayerShadowData", data)
		raise Return(ret)
	else:
		raise Return(0)

@coroutine
def KickoutPlayers(cb):
	from script.gm.defines import IsAuth
	lstPlayer = GetAllPlayers()
	if not lstPlayer:
		cb(1)
		return
	for oPlayer in lstPlayer:
		ret = yield SaveOnePlayer(weakref.proxy(oPlayer))
		if not ret:
			PrintError("%s shutdow save failed"%oPlayer.m_OpenID)
		if not IsAuth(oPlayer.m_OpenID):
			S2COffline(oPlayer.m_OpenID)
	cb(1)

def S2COffline(sOpenID):
	oNetPack = PacketPrepare(S2C_OFFLINE)
	PacketSend(sOpenID, oNetPack)


# NOTE TODO: player中只加必要的接口和属性，尽量减少属性和方法数量，后期数量较多后会使用mixin提升效率并节省空间
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
			"m_TimeLimitData": 	False,
		}

		#需要存盘的数据
		self.m_SendedNum = 0
		self.m_SendedAllNum = 0
		self.m_SendedList = []
		self.m_GetPlpWay = 1		#1-不获取重复的 2-获取重复的
		self.m_TimeLimitData = {}		#限时数据，如 每日固定时间重置，或到某时间点过期的数据（惰性检查，取数据以及load之后检查是否到期，所以访问数据需要使用接口，勿直接访问该数据结构）

	def __repr__(self):
		return "<player(%s) %s %s>" % (self.m_ConnectID, self.m_OpenID, str(self.m_SaveState))

	def FillDefault(self):
		# Load后没有数据的需要赋默认值，否则为None
		if not self.m_SendedNum:
			self.m_SendedNum = 0
		if not self.m_SendedAllNum:
			self.m_SendedAllNum = 0
		if not self.m_SendedList:
			self.m_SendedList = []
		if not self.m_GetPlpWay:
			self.m_GetPlpWay = 1
		if not self.m_TimeLimitData:
			self.m_TimeLimitData = {}

	def AfterLoad(self):
		import copy
		dData = copy.deepcopy(self.m_TimeLimitData)
		for key, tData in dData.items():
			iExpireTime = tData[1]
			if iExpireTime <= GetNowTime():
				self.SetSaveState("m_TimeLimitData", True)
				del self.m_TimeLimitData[key]

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
				data[sAttr] = getattr(self, sAttr, None)
		for sAttr in lstAttr:
			self.SetSaveState(sAttr, False)
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

	def GetPlpWay(self):
		return self.m_GetPlpWay

	def SetPlpWay(self, iWay):
		self.SetSaveState("m_GetPlpWay", True)
		self.m_GetPlpWay = iWay

	def SetTimeLimitData(self, key, val, timelimit):
		"""
		key 获取数据的key key重复时会覆盖数据和过期时间
		val 数据的值
		timelimit 为int时，自己设定过期时间 为string时，"day5"-表示下一次凌晨5点过期 "day0"-表示当日24点过期

		如果需要追加数据，为了通用性，需要先query，增加数据之后再重新set回来，如果只是set则不用query，直接set即可
		"""
		iExpireTime = -1
		if type(timelimit) == int:
			iExpireTime = timelimit
		elif type(timelimit) == str:
			if timelimit == "day5":
				iExpireTime = GetDay5Sec(GetDayNo())
			elif timelimit == "day0":
				iExpireTime = GetDay0Sec(GetDayNo())
			
		if iExpireTime == -1:
			raise Exception("SetTimeLimitData error, timelimit is invalid")
		self.SetSaveState("m_TimeLimitData", True)
		self.m_TimeLimitData[key] = (val, iExpireTime)

	def QueryTimeLimitData(self, key, default = None):
		"""
		获取时会进行过期检查
		key 数据的key
		default 不存在或者过期时，默认返回值
		"""
		if key in self.m_TimeLimitData:
			_, iExpireTime = self.m_TimeLimitData[key]
			if iExpireTime <= GetNowTime():
				self.SetSaveState("m_TimeLimitData", True)
				del self.m_TimeLimitData[key]
		tData = self.m_TimeLimitData.get(key, ())
		if not tData:
			return default
		return tData[0]

	def DeleteTimeLimitData(self, key):
		if key in self.m_TimeLimitData:
			self.SetSaveState("m_TimeLimitData", True)
			del self.m_TimeLimitData[key]


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

def GetAllPlayers():
	global PLAYER_LIST
	return list(PLAYER_LIST.values())

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
