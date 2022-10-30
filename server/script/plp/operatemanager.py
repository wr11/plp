# -*- coding: utf-8 -*-

from myutil.mycorotine import coroutine
from script.plp.datactl import GetDatCtl
from script.common import OpenTips
from script.plp.defines import PUBLISHCNT_DAY, IDTYPE
from script.gameplay.basectl import GetGameCtl
from myutil.myrandom import GetUniqueRandomIDList

import script.player as player
import pubdefines

def Init():
	oPlpManager = GetOperationManager()
	if not pubdefines.GetGlobalManager("plp"):
		pubdefines.SetGlobalManager("plp", oPlpManager)

class CPlp:
	def Load(self, dData):
		self.m_Data = dData

	def Save(self):
		return self.m_Data

class CPlpOeration:
	def __init__(self):
		self.m_DataCtl = GetDatCtl()

	def PublishPlp(self, who, dData):
		if not self.ValidPublishPlp(who, dData):
			return
		oGameCtl = GetGameCtl("IDGenerator")
		if not oGameCtl:
			PrintError("IDGenerator is not available!")
			return
		iID = oGameCtl.GenerateIDByType(IDTYPE)
		dData["id"] = iID
		oPlp = CPlp()
		oPlp.Load(dData)
		self.m_DataCtl.Append(iID, oPlp)
		who.AddPlp(iID)

	def ValidPublishPlp(self, who, dData):
		if not who.CheckPulishCnt(PUBLISHCNT_DAY):
			OpenTips(who.m_OpenID, 1, "", "none", "每天最多发%s个"%PUBLISHCNT_DAY)
			return 0
		sContent = dData["content"]
		if not self.CheckContentIllegal(sContent):
			OpenTips(who.m_OpenID, 1, "", "none", "内容不合规，请重新输入")
			return 0
		return 1

	def CheckContentIllegal(self, sContent):
		return True

	def ValidGetPlp(self, who):
		return True

	def ResetSendedCache(self, who):
		OpenTips(who.m_OpenID, 1, "", "success", "操作成功")
		who.m_SendedToClient = []

	@coroutine
	def GetFivePlp(self, who_proxy):
		sOpenID = who_proxy.m_OpenID
		if not self.ValidGetPlp(who_proxy):
			OpenTips(sOpenID, 1, "", "none", "无法查看")
			return
		oGameCtl = GetGameCtl("IDGenerator")
		if not oGameCtl:
			PrintError("IDGenerator is not available!")
			return
		if not hasattr(who_proxy, "m_SendedToClient"):
			who_proxy.m_SendedToClient = []
		lstSended = getattr(who_proxy, "m_SendedToClient", [])
		iWay = who_proxy.GetPlpWay()
		iMaxID = oGameCtl.GetCurIDByType(IDTYPE)
		if iMaxID == 0:
			return
		iMinID = yield self.m_DataCtl.GetMinID()
		if iMinID == 0:
			return
		lstPlpID = self.GetPlpIDList(iWay, lstSended, iMaxID, iMinID, 5)
		lstPlpData = yield self.m_DataCtl.GetMultiPlpData(lstPlpID)
		PrintDebug("----",lstPlpData)

	def GetPlpIDList(self, iWay, lstSended, iMaxID, iMinID, iCount):
		#待优化，iCount很多时会占很大内存
		if iWay == 1:
			setAll = set(range(iMinID, iMaxID+1))
			setSended = set(lstSended)
			lstSelectable = list(setAll - setSended)
			return GetUniqueRandomIDList(lstSelectable, iCount)
		else:
			return GetUniqueRandomIDList(list(range(iMinID, iMaxID+1)), iCount)

if "g_PlpOeration" not in globals():
	g_PlpOeration = CPlpOeration()

def GetOperationManager():
	return g_PlpOeration