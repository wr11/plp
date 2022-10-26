# -*- coding: utf-8 -*-

from mylog.logcmd import PrintError
from script.common import OpenTips
from pubtool import Functor

import netpackage as np

def ExecGMOrder(sOpenID, oNetPackage):
	sOrder = np.UnpackS(oNetPackage)
	TrueExecGMOrder(sOpenID, sOrder)

def TrueExecGMOrder(sOpenID, sOrder):
	bSuccess = True
	try:
		PrintDebug("excuting GM order: ", sOrder)
		exec(sOrder)
	except Exception as e:
		PrintError(e)
		bSuccess = False

	if not bSuccess:
		OpenTips(sOpenID, 2, "gm_excute", "GM", "error,again?", callback = Functor(GetAnswer, sOrder))
	else:
		OpenTips(sOpenID, 1, "", "success", "GM执行成功")

def GetAnswer(sOrder, who, *args):
	PrintDebug("answer: ",who, args, sOrder)
	sContent = args[0]
	bConfirm = args[1]
	bCancel = args[2]
	if bConfirm:
		TrueExecGMOrder(who.m_OpenID, sOrder)