# -*- coding: utf-8 -*-

from script.gameplay import CGameCtl as CCustomGameCtl, GetGameCtl

PLP_IDTYPE = "plp"

class CGameCtl(CCustomGameCtl):

	def __init__(self):
		self.m_GameName = "plp"
		self.m_SaveAttr = {}