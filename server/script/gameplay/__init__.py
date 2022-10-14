# -*- coding: utf-8 -*-

def Init():
	return

g_GameList = {}

import script.gameplay.plp as plp
import script.gameplay.IDGenerator as IDGenerator

g_GameList["plp"] = plp.CGameCtl
g_GameList["IDGenerator"] = IDGenerator.CGameCtl

class CGameCtl:
	def __init__(self):
		self.m_GameName = ""

	def Init(self):
		pass

	def Save(self):
		pass

	def Load(self, data):
		pass