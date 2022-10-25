# -*- coding: utf-8 -*-

from script.plp.datactl import GetDatCtl

import script.player as player

class CPlpOeration:
	def __init__(self):
		self.m_Data = GetDatCtl()

	def GeneratePlp(self, sOpenID, dData):
		who = player.GetOnlinePlayer(sOpenID)
		if not who:
			return
		sContent = dData.get("Content", "")
		d

if "g_PlpOeration" not in globals():
	g_PlpOeration = CPlpOeration()

def GetOperationManager():
	return g_PlpOeration