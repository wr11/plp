# coding:utf-8

import time
import weakref
import collections
import os

#全局注释
#根路径
SERVER_DIR = os.getcwd()

#根目录名称
SERVER_DIR_ROOT = "server"

#数据发送目标的角色
CLIENT = 1
SERVER = 0

#消息队列类型
MSGQUEUE_SEND = 1
MSGQUEUE_RECV = 2

#mysql游标类型
MYSQL_CURSOR = "Cursor"
MYSQL_DICTCURSOR = "DictCursor"
MYSQL_SSCURSOR = "SSCursor"
MYSQL_SSDICTCURSOR = "SSDictCursor"

#小程序appid,secretkey
APPID = "wx4df313f347893eb8"
SECRETKEY = "f7fef44a65e0678d1302ecf86f3f5925"

#玩家对象弱引用, 异步中使用
def GetPlayerProxy(sOpenID, bOnline = True):
	import script.player as player
	if bOnline:
		who = player.GetOnlinePlayer(sOpenID)
	else:
		who = player.GetPlayer(sOpenID)
	if who:
		who_proxy = weakref.proxy(who)
		return who_proxy
	else:
		return None

#异步后判断弱引用的原始对象是否依然存在
def IsProxyExist(proxy):
	try:
		bool(proxy)
	except:
		return False
	return True

#时间超时管理类
class CTimeOutManager:
	def __init__(self):
		self.m_PreTime = GetNowTime(True)
		self.m_TimeSlot = collections.defaultdict(dict)
		self.m_Flag2TS = {}

	def Push(self, flag, iTime, oTask):		#需要保证flag唯一，否则会有覆盖危险
		if iTime <= 1:
			iTime = 1
		iDDL = GetNowTime(True) + iTime
		dSlot = self.m_TimeSlot[iDDL]
		dSlot[flag] = oTask
		self.m_Flag2TS[flag] = iDDL
  
	def Pop(self, flag):
		if flag not in self.m_Flag2TS:
			return
		iDDL = self.m_Flag2TS[flag]
		dSlot = self.m_TimeSlot[iDDL]
		oTask = dSlot.pop(flag)
		del self.m_Flag2TS[flag]
		return oTask

	def Get(self, flag):
		if flag not in self.m_Flag2TS:
			return None
		iDDL = self.m_Flag2TS[flag]
		dSlot = self.m_TimeSlot[iDDL]
		return dSlot[flag]

	def PopTimeOut(self):
		iNowTime = GetNowTime(True)
		lst = []
		for iTime in range(self.m_PreTime, iNowTime+1):
			if iTime not in self.m_TimeSlot:
				continue
			dSlot = self.m_TimeSlot.pop(iTime)
			for flag in dSlot.keys():
				del self.m_Flag2TS[flag]
			lst.extend(dSlot.values())
		self.m_PreTime = iNowTime
		return lst

	def IsEmpty(self):
		return 1 if not len(self.m_Flag2TS) else 0

#单例模式
class Singleton:
	hasinstance=False
	orig_instance=None
	def __new__(cls):
		if cls.hasinstance==False:
			cls.hasinstance=True
			cls.orig_instance=super().__new__(cls)
			return cls.orig_instance
		else:
			return cls.orig_instance

#管理类基类
class BaseManager(Singleton):
	pass

'''
三种Functor:
Functor: 正常的打包函数类
LiteFuctor：轻量级打包函数类
MyFuncotor：增加了错误的输出栈信息，更容易定位错误的位置
'''

import inspect

class Functor:
	def __init__(self, fn, *args, **kwargs):
		self._fn = fn
		self._args = args
		self._kwargs = kwargs
		self.m_Type = ""

	def __call__(self, *args, **kwargs):
		dKwargs = {}
		dKwargs.update(self._kwargs)
		dKwargs.update(kwargs)
		return self._fn(*(self._args + args), **dKwargs)

class LiteFuctor:
	def __init__(self, fn, *args):
		self._fn = fn
		self._args = args

	def __call__(self, *args):
		return self._fn(*(self._args + args))

class MyFuncotor(Functor):
	def __init__(self, fn, *args, **kwargs):
		Functor.__init__(self, fn, *args, **kwargs)
		self.__m_traceinfo = []
		for _, filename, line, fromcode, _, _ in inspect.stack()[1:]:
			self.__m_traceinfo.append((filename, line, fromcode))

	def __call__(self, *args, **kwargs):
		try:
			return super().__call__(*args, **kwargs)
		except Exception as e:
			PrintDebug('trace' + '-' * 40)
			for filename, line, formcode in self.__m_traceinfo[::-1]:
				PrintDebug(filename, 'line%s'%line, 'in %s '%formcode)
			PrintDebug
			raise e

#全局函数
#全局对象管理
if "g_GloabalManagerDict" not in globals():
	g_GloabalManagerDict = {}
	g_GManagerLimit = {}

def SetGlobalManager(sFlag, oManager, bLimitReplace = True):
	global g_GloabalManagerDict
	global g_GManagerLimit

	oOld = g_GloabalManagerDict.get(sFlag, None)
	if oOld and g_GManagerLimit.get(sFlag, True):
		PrintError("全局管理类 %s 被 %s 替换" % (oOld, oManager))

	g_GloabalManagerDict[sFlag] = oManager
	g_GManagerLimit[sFlag] = bLimitReplace
	if oOld and hasattr(oManager, "OnReplaced"):
		oManager.OnReplaced(oOld)

def DelGlobalManager(sFlag):
	global g_GloabalManagerDict
	global g_GManagerLimit

	if sFlag in g_GloabalManagerDict:
		del g_GloabalManagerDict[sFlag]
	if sFlag in g_GManagerLimit: 
		del g_GManagerLimit[sFlag]

def GetGlobalManager(sFlag):
	global g_GloabalManagerDict
	if sFlag in g_GManagerLimit:
		return g_GloabalManagerDict[sFlag]
	return None

def CallManagerFunc(sFlag, sFunc, *args, **kwargs):
	oManager = GetGlobalManager(sFlag)
	if not oManager:
		raise Exception("无此全局对象 %s" % sFlag)
	func = getattr(oManager, sFunc, None)
	if not func:
		raise Exception("全局对象 %s 中，找不到函数 %s" % (sFlag, sFunc))

	return func(*args, **kwargs)

def GetManagerFunc(sFlag, sFunc):
	oManager = GetGlobalManager(sFlag)
	if not oManager:
		PrintError("无此全局对象 %s" % sFlag)
		return None
	func = getattr(oManager, sFunc, None)
	return func

#----------------time-----------------
Reference_Time = int(time.mktime((2022,1,1,0,0,0,0,0,0)))
if "g_TimeOffset" not in globals():
	g_TimeOffset = 0

def SetTimeOffset(iTimeOffset):
	global g_TimeOffset
	g_TimeOffset += iTimeOffset

def ResetTimeOffset():
	global g_TimeOffset
	g_TimeOffset = 0

def GetNowTime(bReal = False):
	if bReal:
		return int(time.time()) 
	else:
		return int(time.time()) + g_TimeOffset

def TimeStr(iTime = 0):
	if not iTime:
		iTime = GetNowTime()
	oTime = time.localtime(iTime)
	return time.strftime("%Y-%m-%d %H:%M:%S", oTime)

def GetTimeSec(setTime):
	return int(time.mktime(setTime))

def GetDayNo(iTime = 0):
	if not iTime:
		iTime = GetNowTime()
	iDayNo = (iTime - Reference_Time)/3600/24
	return int(iDayNo) + 1

def GetHourNo(iTime = 0):
	if not iTime:
		iTime = GetNowTime()
	iHourNo = (iTime - Reference_Time)/3600
	return int(iHourNo)

def GetMiniteNo(iTime = 0):
	if not iTime:
		iTime = GetNowTime()
	iMiniteNo = (iTime - Reference_Time)/60
	return int(iMiniteNo)

def GetWeekNo(iTime = 0):
	if not iTime:
		iTime = GetNowTime()
	iWeekNo = (iTime - Reference_Time)/3600/24/7
	return int(iWeekNo)+1

def GetMonthNo(iTime = 0):
	if not iTime:
		iTime = GetNowTime()
	setTime = time.localtime(iTime)
	return (setTime[0] - 2000) *100 + setTime[1]

def GetYearNo(iTime = 0):
	if not iTime:
		iTime = GetNowTime()
	setTime = time.localtime(iTime)
	return setTime[0]

def GetSecByMinNo(iNo):
	return iNo * 60 + Reference_Time

def GetSecByHourNo(iNo):
	return iNo * 3600 + Reference_Time

def GetSecByDayNo(iNo):
	return (iNo - 1) * 3600 * 24 + Reference_Time

def GetSecByWeekNo(iNo):
	return (iNo - 1) * 3600 * 24 * 7 + Reference_Time

def GetSecByMonthNo(iNo):
	return int(time.mktime((iNo/100 + 2000, iNo%100, 1, 0, 0, 0, 0, 0, 0)))

def GetSecByYearNo(iNo):
	return int(time.mktime((iNo, 1, 1, 0, 0, 0, 0, 0, 0)))

def GetDay0Sec(iNo):
	if not iNo:
		iNo = GetDayNo() - 1
	return Reference_Time + iNo * 3600 * 24

def GetDay5Sec(iNo):
	return GetDay0Sec(iNo) + 5*3600

def Get5DayNo(iTime):
	if not iTime:
		iTime = GetNowTime()
	return GetDayNo(iTime - 5*3600)