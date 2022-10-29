# -*- coding: utf-8 -*-

from script.gameplay.basectl import CGameCtl as CCustomGameCtl

class CGameCtl(CCustomGameCtl):
	def __init__(self):
		self.m_GameName = "IDGenerator"
		self.m_SaveAttr = {
			"m_IDList" : False,
		}

		self.m_IDList = {}

	def AfterLoad(self):
		if not self.m_IDList:
			self.m_IDList = {}

	def GenerateIDByType(self, sType):
		self.SetSaveState("m_IDList", True)
		if sType not in self.m_IDList:
			self.m_IDList[sType] = 0
		iNum = self.m_IDList[sType]
		iNewID = iNum + 1
		self.m_IDList[sType] = iNewID
		return iNewID

	def FixIDByType(self, sType, iVal):
		self.SetSaveState("m_IDList", True)
		if sType not in self.m_IDList:
			self.m_IDList[sType] = 0
		self.m_IDList[sType] = iVal

	def GetCurIDByType(self, sType):
		return self.m_IDList.get(sType, 0)

	def ResetIDByType(self, sType):
		if sType not in self.m_IDList:
			return
		self.m_IDList[sType] = 0