# -*- coding: utf-8 -*-

from myutil.mycorotine import coroutine, Return

import script.plp as plp
import script.gameplay as gameplay
import script.containers as containers
import script.player as player
import conf
import rpc

# GPS
def Init():
	if conf.IsGPS():
		player.Init()
		plp.Init()
		gameplay.Init()
		containers.Init()

		SetServerState(1)

		PrintNotify("server start finish !")
		LogFileNotify("server", "server start finish!")

def SetServerState(iState):
	iServer, iIndex = conf.GetGate()
	rpc.RemoteCallFunc(iServer, iIndex, None, "script.netcommand.SetServerState", iState)

@coroutine
def GetServerState():
	iServer, iIndex = conf.GetGate()
	ret = yield rpc.AsyncRemoteCallFunc(iServer, iIndex, "script.netcommand.GetServerState")
	raise Return(ret)