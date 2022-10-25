# -*- coding: utf-8 -*-

from timer import Call_out
from myutil.mycorotine import coroutine, WaitMultiFuture

import conf
import rpc


if "g_GameList" not in globals():
	g_GameList = {}

import script.gameplay.plp as plp
import script.gameplay.IDGenerator as IDGenerator

g_GameList["plp"] = plp.CGameCtl
g_GameList["IDGenerator"] = IDGenerator.CGameCtl

def GetGameCtl(sGameName):
	return g_GameList.get(sGameName, None)

@coroutine
def Init():
	global g_GameList
	lstFuture = []
	lstName =[]
	for sGameName, oGamectl in g_GameList.items():
		if oGamectl.m_Loaded:
			continue
		if sGameName in lstName:
			PrintWarning("Game Name %s Repeated!!"%sGameName)
			continue
		lstName.append(sGameName)
		lstAttr = oGamectl.GetSaveAttrList()
		if not lstAttr:
			continue
		iServer, iIndex = conf.GetDBS()
		oFuture = rpc.AsyncRemoteCallFunc(iServer, iIndex, "datahub.manager.LoadGameShadow", sGameName, lstAttr)
		lstFuture = oFuture
	lstData = yield WaitMultiFuture(lstFuture)
	for iIndex, sGameName in enumerate(lstName):
		oGameCtl = GetGameCtl(sGameName)
		if not oGameCtl:
			continue
		if not lstData[iIndex]:
			continue
		oGameCtl.Load(lstData[iIndex])

	Call_out(5*60, "savegame", SaveGames)

def SaveGames():
	# 先不做分帧处理，后面活动多了再做
	global g_GameList
	data = {}
	for sGameName, oGameCtl in g_GameList.items():
		dGameData = oGameCtl.Save()
		if not dGameData:
			continue
		data[sGameName] = dGameData
		if hasattr(oGameCtl, "OnSave"):
			func = oGameCtl.OnSave
			func()
	iServer, iIndex = conf.GetDBS()
	rpc.RemoteCallFunc(iServer, iIndex, None, "datahub.manager.UpdateGameShadowData", data)

class CGameCtl:
	def __init__(self):
		self.m_GameName = ""
		self.m_Loaded = False
		self.m_SaveAttr = {}

	def SetSaveState(self, sAttr, bState):
		self.m_SaveAttr[sAttr] = bState

	def GetAttrNeedSave(self, sAttr):
		return self.m_SaveAttr[sAttr]

	def GetSaveAttrList(self):
		return self.m_SaveAttr.keys()

	def Init(self):
		pass

	def Save(self):
		data = {}
		lstAttr = self.GetSaveAttrList()
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