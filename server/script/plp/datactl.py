# -*- coding: utf-8 -*-

from myutil.mycorotine import Return, coroutine
from script.containers import CListContainer, RegistListContainer

def Init():
	RegistListContainer(GetDatCtl())

class CDataCtl(CListContainer):
	m_TypeName = "tbl_plp"

	@coroutine
	def GetMinID(self):
		ret = yield self.SelectSingleDataFromDB("MIN(plpid)")
		if ret:
			if ret[0]["MIN(plpid)"] is None:
				raise Return(0)
			else:
				raise Return(ret[0]["MIN(plpid)"])
		else:
			raise Return(0)

	@coroutine
	def GetMultiPlpData(self, lstPlpID):
		if not lstPlpID:
			raise Return([])
		ret = yield self.SelectMultiDataFromDB("*", lstPlpID)
		raise Return(ret)

	@coroutine
	def GetPlpCount(self):
		ret = yield self.SelectSingleDataFromDB("COUNT(plpid)")
		if not ret:
			raise Return(0)
		else:
			raise Return(ret[0].get("COUNT(plpid)", 0))

if "g_PlpDataCtl" not in globals():
	g_PlpDataCtl = CDataCtl()

def GetDatCtl():
	return g_PlpDataCtl