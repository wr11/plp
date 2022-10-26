# -*- coding: utf-8 -*-

def Init():
	return

class CDataCtl:
	def __init__(self):
		self.m_Container = []

if "g_PlpDataCtl" not in globals():
	g_PlpDataCtl = CDataCtl()

def GetDatCtl():
	return g_PlpDataCtl