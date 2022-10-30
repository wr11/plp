# -*- coding: utf-8 -*-

from mylog.logcmd import PrintError
from myutil.mycorotine import coroutine
from script.common import OpenTips
from pubtool import Functor

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


def LookGameCtl(who):
	import script.player as player
	from pubdefines import CallManagerFunc, GetPlayerProxy
	import script.gameplay.basectl as gameplay
	# CallManagerFunc("plp", "PublishPlp", who, {"content":"今天很开心", "password":"123456", "location":"china"})
	# gameplay.GetGameCtl("IDGenerator").GenerateIDByType("test")
	print("gm idgenerator", gameplay.GetGameCtl("IDGenerator").m_IDList)
	# who.AddPlp(78)
	# who.RemovePlp(78)
	# who.ResetPlp()
	print("gm playerinfo", who.m_SendedNum, who.m_SendedList, who.m_SendedAllNum, who.m_GetPlpWay)
	CallManagerFunc("plp", "GetFivePlp", GetPlayerProxy(who.m_OpenID))

ORDER = {
	"LookGameCtl": LookGameCtl,
}