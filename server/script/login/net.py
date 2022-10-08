# -*- coding: utf-8 -*-
from myutil.mycorotine import coroutine

import netpackage as np

def NetCommand(who, oNetPackage):
	sSub = np.UnpackS(oNetPackage)
	PrintDebug("the received data is %s" % sSub)
	Handle(who, sSub)

def Handle(who, sSub):
	GetDataFromDs2(sSub)

def GetDataFromDs(sSub):
	import rpc
	oCB = rpc.RpcOnlyCBFunctor(CB_GetDataFromDs, sSub)
	rpc.RemoteCallFunc(1000, 2, oCB, "script.login.net.RTest", 1, sSub, a=2)

def RTest(oResPonse, *args, **kwargs):
	oResPonse(3, {"444":555})
 
def CB_GetDataFromDs(sSub, i, d):
	PrintDebug("rpc end receive result %s:%s %s"%(sSub, i, d))

@coroutine
def GetDataFromDs2(sSub):
	from rpc import AsyncRemoteCallFunc
	ret = yield AsyncRemoteCallFunc(1000, 2, "script.login.net.RTest", 1, sSub, a=2)
	PrintDebug("接收到协程rpc处理结果 %s"%(ret))