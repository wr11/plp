# -*- coding: utf-8 -*-

from script.plp.datactl import GetDatCtl
from script.common import OpenTips
from script.plp.defines import PUBLISHCNT_DAY
from script.gameplay.basectl import GetGameCtl

import script.player as player

class CPlpOeration:
	def __init__(self):
		self.m_Data = GetDatCtl()

	def PublishPlp(self, who, dData):
		if not self.ValidPublishPlp(who, dData):
			return
		oGameCtl = GetGameCtl("IDGenerator")
		if not oGameCtl:
			PrintError("IDGenerator is not available!")
			return
		sID = oGameCtl.GenerateIDByType("plp")
		dData["id"] = sID
		self.m_Data.Append(dData)

	def ValidPublishPlp(self, who, dData):
		if not who.CheckPulishCnt(PUBLISHCNT_DAY):
			OpenTips(who.m_OpenID, 1, "plp_pulish_failed_cnt", "none", "每天最多发%s个"%PUBLISHCNT_DAY)
			return 0
		sContent = dData["content"]
		if not self.CheckContentIllegal(sContent):
			OpenTips(who.m_OpenID, 1, "plp_pulish_failed_cnt", "none", "内容不合规，请重新输入")
			return 0
		return 1

	def CheckContentIllegal(self, sContent):
		return True

if "g_PlpOeration" not in globals():
	g_PlpOeration = CPlpOeration()

def GetOperationManager():
	return g_PlpOeration