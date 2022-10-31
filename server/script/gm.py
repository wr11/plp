# -*- coding: utf-8 -*-

from myutil.mycorotine import coroutine
from script.common import OpenTips
from pubdefines import Functor, CallManagerFunc, GetPlayerProxy, GetDay0Sec, GetNowTime, GetDayNo, GetDay5Sec, SetTimeOffset, TimeStr, ResetTimeOffset

import netpackage as np

def ExecGMOrder(who, oNetPackage):
	sOrder = np.UnpackS(oNetPackage)
	TrueExecGMOrder(who, sOrder)

def TrueExecGMOrder(who, sOrder):
	bSuccess = True
	try:
		PrintNotify("excuting GM order: ", sOrder)
		lstOrder = sOrder.split("-")
		sName = lstOrder[0]
		if sName in ORDER:
			func, sArgs = ORDER[sName]
			if sArgs == "":
				func(who)
			else:
				lstArgs = lstOrder[1:]
				if len(lstArgs) != len(sArgs):
					PrintError("GM Error: function %s args '%s' does not match with input %s"%(func.__name__, sArgs, str(lstArgs)))
					return
				lstRes = []
				for ix in range(len(sArgs)):
					sType = sArgs[ix]
					if sType == "i":
						iVal = eval(lstArgs[ix])
						iVal = int(iVal)
						lstRes.append(iVal)
					elif sType == "s":
						lstRes.append(lstArgs[ix])
					elif sType == "b":
						sVal = lstArgs[ix]
						if sVal in ("1", "True", "true"):
							lstRes.append(True)
						else:
							lstRes.append(False)
					else:
						PrintError("GM Error: unknown args type")
				if len(lstRes) == len(sArgs):
					func(who, *lstRes)
				else:
					PrintError("GM Error: function %s args '%s' convert data type error"%(func.__name__, sArgs))
		else:
			PrintError("GM Error: unknown order %s"%(sOrder))
	except Exception as e:
		PrintError(e)
		bSuccess = False

	if not bSuccess:
		OpenTips(who.m_OpenID, 2, "gm_excute", "GM", "error,again?", callback = Functor(GetAnswer, sOrder))
	else:
		OpenTips(who.m_OpenID, 1, "", "success", "GM执行成功")

def GetAnswer(sOrder, who, *args):
	PrintDebug("answer: ",who, args, sOrder)
	sContent = args[0]
	bConfirm = args[1]
	bCancel = args[2]
	if bConfirm:
		TrueExecGMOrder(who, sOrder)



#GM指令执行函数
def GMExample(who, iVal, sVal, bVal):
	PrintDebug("args test val", iVal, sVal, bVal)
	PrintDebug("args test type", type(iVal), type(sVal), type(bVal))

def GMLookGameCtl(who):
	import script.player as player
	import script.gameplay.basectl as gameplay
	# CallManagerFunc("plp", "PublishPlp", who, {"content":"今天很开心", "password":"123456", "location":"china"})
	# gameplay.GetGameCtl("IDGenerator").GenerateIDByType("test")
	print("gm idgenerator", gameplay.GetGameCtl("IDGenerator").m_IDList)
	# who.AddPlp(78)
	# who.RemovePlp(78)
	# who.ResetPlp()
	print("gm playerinfo", who.m_SendedNum, who.m_SendedList, who.m_SendedAllNum, who.m_GetPlpWay)
	CallManagerFunc("plp", "GetFivePlp", GetPlayerProxy(who.m_OpenID))

def GMTime(who):
	PrintDebug("GetNowTime true", TimeStr(GetNowTime(True)), GetNowTime(True))
	PrintDebug("GetNowTime false", TimeStr(GetNowTime()), GetNowTime())

def GMPushTime(who, iVal):
	SetTimeOffset(24 * 60 * 60)
	PrintDebug("当前时间已推进至：", TimeStr(GetNowTime()), GetNowTime())

def GMResetTimeOffset(who):
	ResetTimeOffset()
	PrintDebug("已恢复真实时间", TimeStr(GetNowTime()), GetNowTime())

def GMSetDay5Data(who, sKey, iVal):
	who.SetTimeLimitData(sKey, iVal, "day5")

def GMQueryDay5Data(who, sKey):
	# PrintDebug(who.QueryTimeLimitData("none", [1,2,3]))
	PrintDebug(who.QueryTimeLimitData(sKey, -1))

ORDER = {
	"GMExample" : (GMExample, "isb"),
	"LookGameCtl": (GMLookGameCtl, ""),
	"TimeInfo" : (GMTime, ""),
	"PushTime" : (GMPushTime, "i"),
	"RealTime" : (GMResetTimeOffset, ""),
	"SetDay5Data" : (GMSetDay5Data, "si"),
	"QueryDay5Data" : (GMQueryDay5Data, "s"),
}

"""
ORDER {指令名称 : (指令函数, 函数参数)}
其中 函数参数 为一个字符串，如果不需要参数则为空字符串
如果需要参数，则按照如下规则填写
1. 字符串每个字符代表一个参数的类型，即参数有5个，则字符串长度为5
2. 字符对照参数类型如下:
i -	int (支持输入算式)
s - str
b - bool (1,true,True为True，其他为False)

客户端指令输入时按照如下格式输入
func-arg1-arg2 ... (客户端指令参数不需要区分数据结构)
"""