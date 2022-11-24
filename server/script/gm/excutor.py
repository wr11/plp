# -*- coding: utf-8 -*-

from myutil.mycorotine import coroutine, Future
from script.common import OpenTips
from pubdefines import Functor, CallManagerFunc, GetPlayerProxy, GetDay0Sec, GetNowTime, GetDayNo, GetDay5Sec, SetTimeOffset, TimeStr, ResetTimeOffset
from script.gm.defines import IsAuth

import netpackage as np
import conf

def ExecGMOrder(who, oNetPackage, iDataHeader):
	sOpenID = who.m_OpenID
	if not IsAuth(sOpenID):
		OpenTips(who.m_OpenID, 1, "", "none", "当前账号无GM权限")
		return
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
					match sType:
						case "i":
							iVal = eval(lstArgs[ix])
							if type(iVal) == int:
								lstRes.append(iVal)
						case "s":
							lstRes.append(lstArgs[ix])
						case "b":
							sVal = lstArgs[ix]
							if sVal in ("1", "True", "true"):
								lstRes.append(True)
							else:
								lstRes.append(False)
						case "d":
							dVal = eval(lstArgs[ix])
							if type(dVal) == dict:
								lstRes.append(dVal)
						case "l":
							lstVal = eval(lstArgs[ix])
							if type(lstVal) == list:
								lstRes.append(lstVal)
						case "t":
							tVal = eval(lstArgs[ix])
							if type(tVal) == tuple:
								lstRes.append(tVal)
						case "e":
							setVal = eval(lstArgs[ix])
							if type(setVal) == set:
								lstRes.append(setVal)
						case _:
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
def GMExample(who, iVal, sVal, bVal, dVal, lstVal, tVal, setVal):
	PrintDebug("args test val", iVal, sVal, bVal, dVal, lstVal, tVal, setVal)
	PrintDebug("args test type", type(iVal), type(sVal), type(bVal), type(dVal), type(lstVal), type(tVal), type(setVal))

def GMSetServerState(who, iState):
	"""
	0-禁止登录 1-允许权限账号登录 2-允许所有账号登录
	"""
	from rpc import RemoteCallFunc
	iServer, iIndex = conf.GetGate()
	RemoteCallFunc(iServer, iIndex, None, "script.netcommand.SetServerState", iState)

def GMSendMsg2All(who, sMsg, iType):
	from script.player import GetAllPlayers
	lstPlayers = GetAllPlayers()
	if not lstPlayers:
		return
	for oPlayer in lstPlayers:
		if iType == 2:
			OpenTips(oPlayer.m_OpenID, iType, "", "提醒", sMsg, bNeedCallBack = False)
		elif iType == 1:
			OpenTips(oPlayer.m_OpenID, iType, "", "none", sMsg)

def GMKickoutOnePlayer(who, sOpenID):
	from script.player import GetOnlinePlayer
	if not GetOnlinePlayer(sOpenID):
		OpenTips(who.m_OpenID, 1, "none", "目标玩家不在线")
		return
	OpenTips(who.m_OpenID, 2, "gm_kickoutoneplayer", "GM", "确认踢该玩家下线吗？", callback = Functor(GMTrueKickoutOnePlayer, sOpenID))

def GMTrueKickoutOnePlayer(sOpenID, who, *args):
	from script.player import S2COffline
	bCancel = args[2]
	if bCancel:
		return
	S2COffline(sOpenID)

def GMShutDown(who):
	OpenTips(who.m_OpenID, 2, "gm_shutdown", "GM", "确认关闭服务器吗？", callback = GMTrueShutDown)

def GMTrueShutDown(who, *args):
	sContent = args[0]
	bConfirm = args[1]
	bCancel = args[2]
	if bCancel:
		return
	GMTrueShutDownStep()

@coroutine
def GMTrueShutDownStep():
	from rpc import AsyncRemoteCallFunc
	import script.player as player
	import script.gameplay as gameplay
	import script.containers as containers
	import mylog.logfile as logfile
	PrintNotify("GM ShutDown Sever Begin!")
	PrintNotify("shutdown step1: set server state 0")
	iServer, iIndex = conf.GetGate()
	ret = yield AsyncRemoteCallFunc(iServer, iIndex, "script.netcommand.SetServerState", 0)
	if not ret:
		PrintNotify("shutdown error: set server state failed, please try again")
		return
	PrintNotify("shutdown step2: kickout players")
	oFuture = Future()
	player.KickoutPlayers(oFuture.set_result)
	ret = yield oFuture
	if not ret:
		PrintNotify("shutdown error: kickout players failed, please try again")
		return
	PrintNotify("shutdown step3 gameplay shutdown")
	ret = yield gameplay.basectl.ShutDown()
	if not ret:
		PrintNotify("shutdown error: gameplay shutdown failed, please try again")
		return
	PrintNotify("shutdown step4 containers shutdown")
	ret = yield containers.ShutDown()
	if not ret:
		PrintNotify("shutdown error: containers shutdown failed, please try again")
		return
	PrintNotify("shutdown step5 logfile shutdown")
	logfile.ShutDown()
	PrintNotify("shutdown step finish! you can now close the process")

def GMLookGameCtl(who):
	import script.player as player
	import script.gameplay.basectl as gameplay
	# CallManagerFunc("plp", "PublishPlp", who, {"content":"今天很开心5", "password":"123456", "location":"china"})
	# gameplay.GetGameCtl("IDGenerator").GenerateIDByType("test")
	print("gm idgenerator", gameplay.GetGameCtl("IDGenerator").m_IDList)
	# who.AddPlp(78)
	# who.RemovePlp(78)
	# who.ResetPlp()
	print("gm playerinfo", who.m_SendedNum, who.m_SendedList, who.m_SendedAllNum, who.m_GetPlpWay)
	CallManagerFunc("plp", "GetFivePlp", GetPlayerProxy(who.m_OpenID))

def GMGetPlayerInfo(who):
	for sAttr in who.GetSaveAttrList():
		PrintDebug("%s : %s"%(sAttr, getattr(who, sAttr, None)))

def GMPublishPlp(who):
	CallManagerFunc("plp", "PublishPlp", who, {"content":"今天很开心3", "password":"123456", "location":"china"})

def GMGet5Plp(who):
	PrintDebug("getway: %s, sended: %s"%(who.m_GetPlpWay, str(getattr(who, "m_SendedToClient", []))))
	CallManagerFunc("plp", "GetFivePlp", GetPlayerProxy(who.m_OpenID))

def GMLookIDList(who):
	import script.gameplay.basectl as gameplay
	PrintDebug("gm idgenerator", gameplay.GetGameCtl("IDGenerator").m_IDList)

def GMTime(who):
	PrintDebug("GetNowTime true", TimeStr(GetNowTime(True)), GetNowTime(True))
	PrintDebug("GetNowTime false", TimeStr(GetNowTime()), GetNowTime())

def GMPushTime(who, iVal):
	SetTimeOffset(iVal)
	PrintDebug("当前时间已推进至：", TimeStr(GetNowTime()), GetNowTime())

def GMResetTimeOffset(who):
	ResetTimeOffset()
	PrintDebug("已恢复真实时间", TimeStr(GetNowTime()), GetNowTime())

def GMSetDay5Data(who, sKey, iVal):
	who.SetTimeLimitData(sKey, iVal, "day5")

def GMQueryDay5Data(who, sKey):
	# PrintDebug(who.QueryTimeLimitData("none", [1,2,3]))
	PrintDebug(who.QueryTimeLimitData(sKey, -1))

def GMResetPlpSendedCache(who):
	CallManagerFunc("plp", "ResetSendedCache", who)

def GMSetGetPlpWay(who, iWay):
	who.SetPlpWay(iWay)
	PrintDebug("当前plp获取方式：", who.GetPlpWay())

def GMGetPlpCount(who):
	CallManagerFunc("plp", "GetPlpCount")

ORDER = {
	"GMExample" : (GMExample, "isbdlte"),
	"SetServerState" : (GMSetServerState, "i"),
	"SendMsg2All" : (GMSendMsg2All, "si"),
	"KickoutOnePlayer" : (GMKickoutOnePlayer, "s"),
	"ShutDown" : (GMShutDown, ""),
	"LookGameCtl": (GMLookGameCtl, ""),
	"TimeInfo" : (GMTime, ""),
	"PushTime" : (GMPushTime, "i"),
	"RealTime" : (GMResetTimeOffset, ""),
	"SetDay5Data" : (GMSetDay5Data, "si"),
	"QueryDay5Data" : (GMQueryDay5Data, "s"),
	"ResetPlpSendedCache" : (GMResetPlpSendedCache, ""),
	"SetGetPlpWay" : (GMSetGetPlpWay, "i"),
	"GetPlayerInfo" : (GMGetPlayerInfo, ""),
	"PublishPlp" : (GMPublishPlp, ""),
	"Get5Plp" : (GMGet5Plp, ""),
	"LookIDList" : (GMLookIDList, ""),
	"GetPlpCount" : (GMGetPlpCount, ""),
}

"""
ORDER {指令名称 : (指令函数, 函数参数)}
其中 函数参数 为一个字符串，如果不需要参数则为空字符串
如果需要参数，则按照如下规则填写
1. 字符串每个字符代表一个参数的类型，即参数有5个，则字符串长度为5
2. 字符对照参数类型如下:
i -	int (支持输入算式)
s - str (客户端输入时不需要加引号)
b - bool (1,true,True为True，其他为False)
d - dict (客户端输入时按照字典格式输入即可 {1:2,...})
l - list (客户端输入时按照列表格式输入即可 [1,2,...])
t - tuple (客户端输入时按照元祖格式输入即可 (1,2,...))
e - set (客户端输入时按照集合格式输入即可 {1,2,...})

如需要获取玩家对象，则传入openid，在指令函数中使用GetOnlinePlayer来获取

客户端指令输入时按照如下格式输入
func-arg1-arg2 ... (客户端指令参数不需要区分数据结构)
"""