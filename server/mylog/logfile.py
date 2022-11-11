# -*- coding: utf-8 -*-

"""
文件日志

记录日志为缓存记录，不会立即记录（想要直接记录可以调用FlushLogFile或者关服时会主动记录一次）
LogFileDebug
LogFileWarning
LogFileError
LogFileStack
LogFileNotify
接口均加入内置方法，使用时无需import
"""

import conf
import time
import traceback
import os
import timer

if "LOCAL_THREAD" not in globals():
	LOCAL_THREAD = ""

if "LOCAL_FLAG" not in globals():
	LOCAL_FLAG = ""

if os.name == "nt":
	DELIMITER = "\\"
else:
	DELIMITER = "/"

LOG_FILE_ROOT_PATH = "log%sserverlog"%(DELIMITER)
DEBUG_DIR = "debug"
WARNING_DIR = "warring"
ERROR_DIR = "error"
STACK_DIR = "stack"
NOTIFY_DIR = "notify"

TYPE2DESC = {
	DEBUG_DIR : "DEBUG",			#只在测试环境中打印，用于 测试类信息
	WARNING_DIR : "WARNING",		#正式/测试均可用，用于 警告类信息
	ERROR_DIR : "ERROR",			#正式/测试均可用，用于 错误类信息
	STACK_DIR : "STACK",			#只在测试环境中打印，用于 堆栈类信息
	NOTIFY_DIR : "NOTIFY",			#正式/测试均可用，用于 通知类信息
}

class CLogFileManager:
	def __init__(self):
		self.m_LogList = {}

	def Init(self):
		timer.Call_out(5, "dologfile", self.DoLogFile)

	def AddLog(self, sType, sFile, sMsg):
		if sType not in self.m_LogList:
			self.m_LogList[sType] = {}
		if sFile not in self.m_LogList[sType]:
			self.m_LogList[sType][sFile] = []
		self.m_LogList[sType][sFile].append(sMsg)

	def DoLogFile(self, bAuto = True):
		if timer.GetTimer("dologfile"):
			timer.Remove_Call_out("dologfile")
		if not self.m_LogList and bAuto:
			timer.Call_out(5, "dologfile", self.DoLogFile)
			return
		for sDir, dData in self.m_LogList.items():
			if not dData:
				continue
			for sFile, lstMsg in dData.items():
				for sMsg in lstMsg:
					try:
						sFilePath = "%s%s%s%s%s.log"%(LOG_FILE_ROOT_PATH, DELIMITER, sDir, DELIMITER, sFile)
						with open(sFilePath, "a") as f:
							f.write("%s\n"%sMsg)
					except Exception as e:
						PrintError("logfile %s %s %s error"%(sDir, sFile, sMsg), e)
						continue
		self.m_LogList = {}

		if bAuto:
			timer.Call_out(5, "dologfile", self.DoLogFile)

if "g_LogFileManager" not in globals():
	g_LogFileManager = CLogFileManager()

def ShutDown():
	global g_LogFileManager
	g_LogFileManager.DoLogFile(False)

def FlushLogFile():
	global g_LogFileManager
	g_LogFileManager.DoLogFile(True)

def Init(sThread):
	global LOCAL_FLAG, LOCAL_THREAD, g_LogFileManager
	sProcessName, iIndex = conf.GetProcessName(), conf.GetProcessIndex()
	LOCAL_FLAG = "%s_%s"%(sProcessName, iIndex)
	LOCAL_THREAD = sThread
	import builtins
	iterGlobalKey = globals().keys()
	for sKey in iterGlobalKey:
		if sKey.startswith("LogFile"):
			builtins.__dict__[sKey] = globals()[sKey]

	InitLogFilePath()

	g_LogFileManager.Init()

	PrintNotify("Logger File inited")

def InitLogFilePath():
	global LOG_FILE_ROOT_PATH
	sCurPath = os.getcwd()
	sLogFilePath = "%s%s%s"%(sCurPath, DELIMITER, LOG_FILE_ROOT_PATH)
	lstPath = [DEBUG_DIR, WARNING_DIR, ERROR_DIR, STACK_DIR, NOTIFY_DIR]
	for sDirName in lstPath:
		sPath = "%s%s%s"%(sLogFilePath, DELIMITER, sDirName)
		if not os.path.exists(sPath):
			os.makedirs(sPath)

def GetCommonLogHeader(sDir):
	global LOCAL_FLAG, LOCAL_THREAD
	sTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	lstTraceMsg = traceback.format_stack()[-3].split(",")
	sFile = lstTraceMsg[0].replace("\\", "/").split("/")[-1][:-4]	#[:-4]去掉多余的.py"
	sLine = lstTraceMsg[1].split(" ")[2]
	sFormatTime = "[%s]"%sTime
	sFormatProc = "[%s:%s]"%(LOCAL_FLAG, LOCAL_THREAD)
	sFormatType = "[%s]"%TYPE2DESC[sDir]
	sFormatLocate = "[%s:%s]"%(sFile, sLine)
	return "%s%s%s%s"%(sFormatTime, sFormatProc, sFormatLocate, sFormatType)

def LogFileDebug(sFile, sMsg):
	global g_LogFileManager
	if not conf.IsDebug():
		return
	sCommonHeader = GetCommonLogHeader(DEBUG_DIR)
	g_LogFileManager.AddLog(DEBUG_DIR, sFile, sCommonHeader + sMsg)

def LogFileWarning(sFile, sMsg):
	global g_LogFileManager
	sCommonHeader = GetCommonLogHeader(WARNING_DIR)
	g_LogFileManager.AddLog(WARNING_DIR, sFile, sCommonHeader + sMsg)

def LogFileError(sFile, sMsg):
	global g_LogFileManager
	sCommonHeader = GetCommonLogHeader(ERROR_DIR)
	g_LogFileManager.AddLog(ERROR_DIR, sFile, sCommonHeader + sMsg)

def LogFileStack(sFile, sMsg):
	global g_LogFileManager
	if not conf.IsDebug():
		return
	sCommonHeader = GetCommonLogHeader(STACK_DIR)
	g_LogFileManager.AddLog(STACK_DIR, sFile, sCommonHeader + sMsg)

def LogFileNotify(sFile, sMsg):
	global g_LogFileManager
	sCommonHeader = GetCommonLogHeader(NOTIFY_DIR)
	g_LogFileManager.AddLog(NOTIFY_DIR, sFile, sCommonHeader + sMsg)