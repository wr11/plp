# -*- coding: utf-8 -*-

from mylog.logcmd import PrintError
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
		PrintDebug("excuting GM order: ", sOrder)
		if sOrder in ORDER:
			ORDER[sOrder](who)
		else:
			exec(sOrder)
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
	# PrintDebug("GetDayNo", GetDayNo())
	# PrintDebug("GetDay0Sec", GetDay0Sec(GetDayNo()))
	# PrintDebug("GetDay5Sec", GetDay5Sec(GetDayNo()))

def GMPushTime(who):
	SetTimeOffset(24 * 60 * 60)
	PrintDebug("当前时间已推进至：", TimeStr(GetNowTime()), GetNowTime())

def GMResetTimeOffset(who):
	ResetTimeOffset()
	PrintDebug("已恢复真实时间", TimeStr(GetNowTime()), GetNowTime())

def GMSetTimeLimitData(who):
	who.SetTimeLimitData("test", 999, "day5")

def GMQueryTimeLimitData(who):
	# PrintDebug(who.QueryTimeLimitData("none", [1,2,3]))
	PrintDebug(who.QueryTimeLimitData("test", [1,2,3]))

ORDER = {
	"LookGameCtl": GMLookGameCtl,
	"TimeInfo" : GMTime,
	"PushTime" : GMPushTime,
	"RealTime" : GMResetTimeOffset,
	"SetTimeLimitData" : GMSetTimeLimitData,
	"QueryTimeLimitData" : GMQueryTimeLimitData,
}