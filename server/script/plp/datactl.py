# -*- coding: utf-8 -*-

def Init():
	return

class CDataCtl:
	pass

if "g_PlpDataCtl" not in globals():
	g_PlpDataCtl = CDataCtl()

def GetDatCtl():
	return g_PlpDataCtl