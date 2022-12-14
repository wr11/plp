# -*- coding: utf-8 -*-

from myutil.mycorotine import coroutine, Return
from script.plp.datactl import GetDatCtl
from script.common import OpenTips
from script.plp.defines import PUBLISHCNT_DAY, IDTYPE, PLP_PUBLISH_FLAG, PLP_GET_FLAG, GETCNT_DAY, CAN_EMPTY
from script.gameplay.basectl import GetGameCtl
from myutil.myrandom import GetUniqueRandomIDList
from protocol import CS_GETPZ

import script.player as player
import pubdefines
import netpackage as np

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
		for key,val in dData.items():
			if not val and key not in CAN_EMPTY:
				OpenTips(who.m_OpenID, 1, "", "none", "请填写完整内容")
				return
		iID = oGameCtl.GenerateIDByType(IDTYPE)
		dData["id"] = iID
		dData["user"] = who.m_OpenID
		oPlp = CPlp()
		oPlp.Load(dData)
		self.m_DataCtl.Append(iID, oPlp)
		who.AddPlp(iID)
		iOldCnt = who.QueryTimeLimitData(PLP_PUBLISH_FLAG, 0)
		iOldCnt += 1
		who.SetTimeLimitData(PLP_PUBLISH_FLAG, iOldCnt, "day5")
		OpenTips(who.m_OpenID, 1, "", "success", "发布成功")

	def ValidPublishPlp(self, who, dData):
		iCnt = who.QueryTimeLimitData(PLP_PUBLISH_FLAG, 0)
		if iCnt >= PUBLISHCNT_DAY:
			OpenTips(who.m_OpenID, 1, "", "none", "每天最多发%s个"%PUBLISHCNT_DAY)
			return 0
		sContent = dData["content"]
		if not self.CheckContentIllegal(sContent):
			OpenTips(who.m_OpenID, 1, "", "none", "内容不合规，请重新输入")
			return 0
		return 1

	def CheckContentIllegal(self, sContent):
		return True

	def ValidGetPlp(self, who_proxy):
		iCnt = who_proxy.QueryTimeLimitData(PLP_GET_FLAG, 0)
		if iCnt >= GETCNT_DAY:
			OpenTips(who_proxy.m_OpenID, 1, "", "none", "每天最浏览%s个"%GETCNT_DAY)
			return 0
		return 1

	def ResetSendedCache(self, who):
		OpenTips(who.m_OpenID, 1, "", "success", "操作成功")
		who.m_SendedToClient = []

	@coroutine
	def GetFivePlp(self, who_proxy):
		sOpenID = who_proxy.m_OpenID
		if not self.ValidGetPlp(who_proxy):
			OpenTips(sOpenID, 1, "", "none", "无法查看")
			raise Return({})
		oGameCtl = GetGameCtl("IDGenerator")
		if not oGameCtl:
			PrintError("IDGenerator is not available!")
			raise Return({})
		if not hasattr(who_proxy, "m_SendedToClient"):
			who_proxy.m_SendedToClient = []
		lstSended = getattr(who_proxy, "m_SendedToClient", [])
		iWay = who_proxy.GetPlpWay()
		iMaxID = oGameCtl.GetCurIDByType(IDTYPE)
		if iMaxID == 0:
			raise Return({})
		iMinID = yield self.m_DataCtl.GetMinID()
		if iMinID == 0:
			raise Return({})
		iCnt = max(0, (GETCNT_DAY-who_proxy.QueryTimeLimitData(PLP_GET_FLAG, 0)))
		iTrueCnt = min(iCnt, 5)
		lstPlpID = self.GetPlpIDList(iWay, lstSended, iMaxID, iMinID, iTrueCnt)
		lstNewSend = list(set(lstPlpID) | set(lstSended))
		setattr(who_proxy, "m_SendedToClient", lstNewSend)
		lstPlpData = yield self.m_DataCtl.GetMultiPlpData(lstPlpID)
		PrintDebug("----",lstPlpData)
		if not pubdefines.IsProxyExist(who_proxy):
			raise Return({})
		iLen = len(lstPlpData)
		iOldCnt = who_proxy.QueryTimeLimitData(PLP_GET_FLAG, 0)
		iOldCnt += iLen
		# who_proxy.SetTimeLimitData(PLP_GET_FLAG, iOldCnt, "day5")
		self.S2CSendPlpInfo(who_proxy.m_OpenID, lstPlpData)
		raise Return(lstPlpData)

	def GetPlpIDList(self, iWay, lstSended, iMaxID, iMinID, iCount):
		#待优化，iCount很多时会占很大内存
		if iWay == 1:
			setAll = set(range(iMinID, iMaxID+1))
			setSended = set(lstSended)
			lstSelectable = list(setAll - setSended)
			return GetUniqueRandomIDList(lstSelectable, iCount)
		else:
			return GetUniqueRandomIDList(list(range(iMinID, iMaxID+1)), iCount)

	@coroutine
	def GetPlpCount(self):
		ret = yield self.m_DataCtl.GetPlpCount()
		PrintDebug(ret)


	def S2CSendPlpInfo(self, sOpenID, data):
		oNetPack = np.PacketPrepare(CS_GETPZ)
		np.PacketAddJSON(data, oNetPack)
		np.PacketSend(sOpenID, oNetPack)

if "g_PlpOeration" not in globals():
	g_PlpOeration = CPlpOeration()

def GetOperationManager():
	return g_PlpOeration