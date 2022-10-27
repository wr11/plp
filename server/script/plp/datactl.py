# -*- coding: utf-8 -*-

from myutil.mycorotine import Return, coroutine
from script.containers import CListContainer, RegistListContainer

def Init():
	RegistListContainer(GetDatCtl())
	return

class CDataCtl(CListContainer):
	m_TypeName = "tbl_plp"

	@coroutine
	def GetMinID(self):
		ret = yield self.SelectDataFromDB("MIN(plpid)")
		raise Return(ret)

if "g_PlpDataCtl" not in globals():
	g_PlpDataCtl = CDataCtl()

def GetDatCtl():
	return g_PlpDataCtl