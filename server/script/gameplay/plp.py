# -*- coding: utf-8 -*-

from script.gameplay import CGameCtl as CCustomGameCtl

class CGameCtl(CCustomGameCtl):
	def __init__(self):
		self.m_GameName = "plp"
		self.m_SaveAttr = {
			"m_PlpList" : False
		}

		self.m_PlpList = {}

	def OnSave(self):
		self.SetSaveState("m_PlpList", False)
		self.m_PlpList = {}