# -*- coding: utf-8 -*-

from timer import Call_out, Remove_Call_out, GetTimer
from myutil.mycorotine import Return, coroutine, WaitMultiFuture

import conf
import rpc

INTERVAL_SAVEGAME = 6

if "g_GameList" not in globals():
	g_GameList = {}

def GetGameCtl(sGameName):
	return g_GameList.get(sGameName, None)

def InitGameList():
	global g_GameList

	import script.gameplay.IDGenerator as IDGenerator

	g_GameList["IDGenerator"] = IDGenerator.CGameCtl()

@coroutine
def Init():
	InitGameList()
	global g_GameList
	lstFuture = []
	lstName =[]
	for sGameName, oGamectl in g_GameList.items():
		oGamectl.Init()
		if getattr(oGamectl, "m_Loaded", 0):
			continue
		if sGameName in lstName:
			PrintWarning("Game Name %s Repeated!!"%sGameName)
			continue
		lstAttr = oGamectl.GetSaveAttrList(bList = True)
		if not lstAttr:
			continue
		lstName.append(sGameName)
		iServer, iIndex = conf.GetDBS()
		oFuture = rpc.AsyncRemoteCallFunc(iServer, iIndex, "datahub.manager.LoadGameShadow", sGameName, lstAttr)
		lstFuture.append(oFuture)
	lstData = yield WaitMultiFuture(lstFuture)
	for iIndex, sGameName in enumerate(lstName):
		oGameCtl = GetGameCtl(sGameName)
		if not oGameCtl:
			continue
		oGameCtl.Load(lstData[iIndex])
		oGameCtl.m_Loaded = True
		oGameCtl.FillDefault()
		oGamectl.AfterLoad()

	Call_out(INTERVAL_SAVEGAME, "savegame", SaveGames)

def SaveGames():
	# 先不做分帧处理，后面活动多了再做
	global g_GameList
	data = {}
	for sGameName, oGameCtl in g_GameList.items():
		if not getattr(oGameCtl, "m_Loaded", 0):
			continue
		dGameData = oGameCtl.Save()
		if not dGameData:
			continue
		data[sGameName] = dGameData
		if hasattr(oGameCtl, "OnSave"):
			oGameCtl.OnSave()
	iServer, iIndex = conf.GetDBS()
	rpc.RemoteCallFunc(iServer, iIndex, None, "datahub.manager.UpdateGameShadowData", data)
	Call_out(INTERVAL_SAVEGAME, "savegame", SaveGames)

@coroutine
def ShutDown():
	global g_GameList
	if GetTimer("savegame"):
		Remove_Call_out("savegame")
	data = {}
	for sGameName, oGameCtl in g_GameList.items():
		if not getattr(oGameCtl, "m_Loaded", 0):
			continue
		dGameData = oGameCtl.Save()
		if not dGameData:
			continue
		data[sGameName] = dGameData
	if not data:
		raise Return(1)
	iServer, iIndex = conf.GetDBS()
	ret = yield rpc.AsyncRemoteCallFunc(iServer, iIndex, "datahub.manager.UpdateGameShadowData", data)
	raise Return(ret)

class CGameCtl:
	def __init__(self):
		self.m_GameName = ""
		self.m_Loaded = False
		self.m_SaveAttr = {}

	def SetSaveState(self, sAttr, bState):
		self.m_SaveAttr[sAttr] = bState

	def GetAttrNeedSave(self, sAttr):
		return self.m_SaveAttr[sAttr]

	def GetSaveAttrList(self, bList = False):
		if not bList:
			return self.m_SaveAttr.keys()
		else:
			return list(self.m_SaveAttr.keys())

	def Init(self):
		pass

	def FillDefault(self):
		# 用于填充默认值，否则Load后默认为None
		pass

	def AfterLoad(self):
		pass

	def Save(self):
		data = {}
		lstAttr = self.GetSaveAttrList()
		if not lstAttr:
			return data
		for sAttr in lstAttr:
			if self.GetAttrNeedSave(sAttr):
				self.SetSaveState(sAttr, False)
				data[sAttr] = getattr(self, sAttr, None)
			else:
				continue
		return data

	def Load(self, data):
		if not data:
			return
		for sAttr, val in data.items():
			setattr(self, sAttr, val)