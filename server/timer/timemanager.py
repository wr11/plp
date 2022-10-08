# -*- coding: utf-8 -*-

import threading
import pubtool
import pubdefines
import pubtool

class CTimerManager(pubtool.Singleton):
	def __init__(self):
		self.m_Map = {}

	def _CreateTimer(self, iTime, oFunc, *args, **kwargs):
		oTimer = threading.Timer(iTime, oFunc, *args, **kwargs)
		return oTimer

	def _Execute(self, iTime, oFunc, sFlag, *args, **kwargs):
		self.Remove_Call_out(sFlag)
		try:
			oFunc(*args, **kwargs)
		except Exception as e:
			self.Call_out(iTime, sFlag, oFunc)
			PrintError("timer %s excute error"%(sFlag))
			raise

	def Call_out(self, iTime, sFlag, oFunc, *args, **kwargs):
		oExecFunc = pubtool.Functor(self._Execute, iTime, oFunc, sFlag)
		oTimer = self._CreateTimer(iTime, oExecFunc, *args, **kwargs)
		self.m_Map[sFlag] = oTimer
		oTimer.start()

	def Remove_Call_out(self, sFlag):
		if sFlag not in self.m_Map:
			return
		self.m_Map[sFlag].cancel()
		del self.m_Map[sFlag]

	def GetTimer(self, sFlag):
		return self.m_Map.get(sFlag, None)

if "g_Timer" not in globals():
	g_Timer = CTimerManager()

def Call_out(iTime, sFlag, oFunc, *args, **kwargs):
	g_Timer.Call_out(iTime, sFlag, oFunc, *args, **kwargs)

def Remove_Call_out(sFlag):
	g_Timer.Remove_Call_out(sFlag)

def GetTimer(sFlag):
	g_Timer.GetTimer(sFlag)