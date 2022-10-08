#coding=utf-8
import time

NODE_SIZE = 256
WHELL_SIZE = 16

class CNode(object):
	def __init__(self, cbfunc=None, iExpire=0):
		self.m_Prev = self
		self.m_Next = self
		self.m_Expire = iExpire
		self.m_CB = cbfunc

class CWhell(object):
	def __init__(self, iNodeSize=NODE_SIZE):
		self.m_NodeList = [CNode() for i in range(iNodeSize)]
		self.m_NodeSize = iNodeSize

	def AddEndNode(self, iNodeIdx, oNode):
		oHead = self.m_NodeList[iNodeIdx]
		oEndNode = oHead.m_Prev
		oNode.m_Next = oEndNode.m_Next
		oEndNode.m_Next = oNode
		oNode.m_Prev = oEndNode

	def AddFrontNode(self, iNodeIdx, oNode):
		oHead = self.m_NodeList[iNodeIdx]
		oFrontNode = oHead.m_Next
		oNode.m_Prev = oFrontNode.m_Prev
		oNode.m_Next = oFrontNode
		oFrontNode.m_Prev = oNode

	def PopFirstNodes(self):
		lstFirstNodes = self.m_NodeList[0]
		del self.m_NodeList[0]
		self.m_NodeList.append(CNode())
		return lstFirstNodes

class CTimer(object):
	def __init__(self, iInterval, iCurrTime, iWhellSize=WHELL_SIZE):
		self.m_CurrTime = 0
		self.m_LastTime = 0
		self.m_Interval = iInterval
		self.m_Remainder = 0
		self.m_WhellList = [CWhell() for i in range(iWhellSize)]
		self.m_WhellSize = iWhellSize

def _RemoveNode(oNode):
	oNode.m_Prev.m_Next = oNode.m_Next
	oNode.m_Next.m_Prev = oNode.m_Prev


def GetNowTime():
	return int(time.time() * 1000)

def _TimerAdd(oNode):
	iWholeNodeIdx = max(0, oNode.m_Expire - g_Timer.m_CurrTime - g_Timer.m_Interval)
	iMaxWhellNodeIdx = g_Timer.m_Interval

	for iWheelIdx, oWhell in enumerate(g_Timer.m_WhellList):
		iTmpNodeIdx = iMaxWhellNodeIdx * oWhell.m_NodeSize
		if iWholeNodeIdx <  iTmpNodeIdx:
			iNodeIdx = iWholeNodeIdx // iMaxWhellNodeIdx
			oWhell.AddEndNode(iNodeIdx, oNode)
			return True
		iMaxWhellNodeIdx = iTmpNodeIdx
	return False

def _TimerTick():
	g_Timer.m_CurrTime += g_Timer.m_Interval
	
	iWholeWhellTime = g_Timer.m_Interval
	for iWhellIdx, oWhell in enumerate(g_Timer.m_WhellList):
		iTmpWhellTime = iWholeWhellTime * oWhell.m_NodeSize
		if g_Timer.m_CurrTime % iTmpWhellTime != 0:
			break
		if iWhellIdx >= g_Timer.m_WhellSize:
			continue
		oNextWhell = g_Timer.m_WhellList[iWhellIdx + 1]
		for oNode in oNextWhell.PopFirstNodes():
			_TimerAdd(oNode)

	
	oHeadWhell = g_Timer.m_WhellList[0]
	iExpiredNodeIdx = g_Timer.m_CurrTime % oHeadWhell.m_NodeSize
	for i in range(iExpiredNodeIdx):
		for oNode in oHeadWhell.PopFirstNodes():
			oNode.m_CB()
	
def TimerUpdate(iCurrTime):
	if iCurrTime <= g_Timer.m_LastTime:
		return
	iDiff = iCurrTime - g_Timer.m_LastTime + g_Timer.m_Remainder
	iInterval = g_Timer.m_Interval
	g_Timer.m_LastTime = iCurrTime

	while iDiff >= iInterval:
		iDiff -= iInterval
		_TimerTick()
	g_Timer.m_Remainder = iDiff

def Call_Out(iTime, cbfunc, sFlag="global"):
	if iTime <= 0:
		cbfunc()
		return
	oNode = CNode(cbfunc, iTime + GetNowTime())
	if not _TimerAdd(oNode):
		raise Exception("Out of max timer limit: %s:%s" % (sFlag, iTime))
	g_TimerMap.setdefault(sFlag, {})
	g_TimerMap[sFlag][id(oNode)] = oNode

def Remove_Call_Out(sFlag):
	if sFlag not in g_TimerMap:
		return
	dNode = g_TimerMap[sFlag]
	del g_TimerMap[sFlag]
	for oNode in dNode.itervalues():
		_RemoveNode(oNode)

def Find_Call_Out(sFlag):
	return sFlag in g_TimerMap

if "g_Timer" not in globals():
	g_Timer = CTimer(1, GetNowTime())
if "g_TimerMap" not in globals():
	g_TimerMap = {}

all = [Call_Out, Remove_Call_Out, Find_Call_Out, GetNowTime, TimerUpdate]