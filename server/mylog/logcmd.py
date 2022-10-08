# -*- coding: utf-8 -*-

from colorama import init

import conf
import time
import traceback

if "LOCAL_THREAD" not in globals():
	LOCAL_THREAD = ""

if "LOCAL_FLAG" not in globals():
	LOCAL_FLAG = ""

#PrintDebug type
DEBUG = 1
WARNING = 2
ERROR = 3
STACK = 4
NOTIFY = 5

TYPE2DESC = {
	DEBUG : "DEBUG",			#只在测试环境中打印，用于 测试类信息
	WARNING : "WARNING",		#正式/测试均可用，用于 警告类信息
	ERROR : "ERROR",			#正式/测试均可用，用于 错误类信息
	STACK : "STACK",			#测试环境可用，用于 堆栈类信息
	NOTIFY : "NOTIFY",			#正式/测试均可用， 用于 通知类信息
}

def Init(sThread):
	global LOCAL_FLAG, LOCAL_THREAD
	sProcessName, iIndex = conf.GetProcessName(), conf.GetProcessIndex()
	LOCAL_FLAG = "%s_%s"%(sProcessName, iIndex)
	LOCAL_THREAD = sThread
	import builtins
	iterGlobalKey = globals().keys()
	for sKey in iterGlobalKey:
		if sKey.startswith("Print"):
			builtins.__dict__[sKey] = globals()[sKey]

	init(autoreset=True)

	PrintNotify("Logger inited")

def GetCommonLogHeader(iType):
	global LOCAL_FLAG, LOCAL_THREAD
	sTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	lstTraceMsg = traceback.format_stack()[-3].split(",")
	sFile = lstTraceMsg[0].replace("\\", "/").split("/")[-1][:-4]	#[:-4]去掉多余的.py"
	sLine = lstTraceMsg[1].split(" ")[2]
	sFormatTime = "[%s]"%sTime
	sFormatProc = "[%s:%s]"%(LOCAL_FLAG, LOCAL_THREAD)
	sFormatType = "[%s]"%TYPE2DESC[iType]
	sFormatLocate = "[%s:%s]"%(sFile, sLine)
	return "%s%s%s%s"%(sFormatTime, sFormatProc, sFormatLocate, sFormatType)


def PrintDebug(*args):
	if not conf.IsDebug():
		return
	args = [str(i) for i in args]
	sHeader = GetCommonLogHeader(DEBUG)
	sMsg = "%s %s"%(sHeader, " ".join(args))
	print("\033[0;35;40m%s"%sMsg,"\033[0m")

def PrintError(*args):
	args = [str(i) for i in args]
	sHeader = GetCommonLogHeader(ERROR)
	sMsg = "%s %s"%(sHeader, " ".join(args))
	print("\033[0;31;40m%s"%sMsg,"\033[0m")

def PrintWarning(*args):
	args = [str(i) for i in args]
	sHeader = GetCommonLogHeader(WARNING)
	sMsg = "%s %s"%(sHeader, " ".join(args))
	print("\033[0;34;40m%s"%sMsg,"\033[0m")

def PrintStack(*args):
	if not conf.IsDebug():
		return
	args = [str(i) for i in args]
	sHeader = GetCommonLogHeader(STACK)
	sMsg = "%s %s"%(sHeader, " ".join(args))
	print("\033[0;32;40m%s"%sMsg,"\033[0m")
	traceback.print_stack()

def PrintNotify(*args):
	args = [str(i) for i in args]
	sHeader = GetCommonLogHeader(NOTIFY)
	sMsg = "%s %s"%(sHeader, " ".join(args))
	print("\033[0;37;40m%s"%sMsg,"\033[0m")

#颜色
#开头格式符号：\033[显示方式;前景色;背景色m 
#结尾格式符号：\033[0m
#完整格式符号： \033[显示方式;前景色;背景色m要打印的文字\033[0m
#开头部分的三个参数：显示方式，前景色，背景色是可选参数，可以只写其中的某一个；
#由于表示三个参数不同含义的数值都是唯一的没有重复的，所以三个参数的书写先后顺序没有固定要求，系统都能识别

#显示方式 0-默认值 1-高亮即加粗 4-下划线 7-反显
#前景色 30-黑色 31-红色 32-绿色 33-黄色 34-蓝色 35-梅色 36-青色 37-白色
#背景色 40-黑色 41-红色 42-绿色 43-黄色 44-蓝色 45-梅色 46-青色 47-白色