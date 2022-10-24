# -*- coding: utf-8 -*-

from script.plp.datactl import GetDatCtl

class CPlpOeration:
	def __init__(self):
		self.m_Data = GetDatCtl()

	def GeneratePlp(self, who, dData):
		pass

if "g_PlpOeration" not in globals():
	g_PlpOeration = CPlpOeration()

def GetOperationManager():
	return g_PlpOeration