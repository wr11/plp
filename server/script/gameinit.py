# -*- coding: utf-8 -*-
import script.plp as plp
import script.gameplay as gameplay
import script.containers as containers
import script.player as player
import conf
import rpc

def Init():
	if conf.IsGPS():
		player.Init()
		plp.Init()
		gameplay.Init()
		containers.Init()

		SetServerState(1)

def SetServerState(iState):
	iServer, iIndex = conf.GetGate()
	rpc.RemoteCallFunc(iServer, iIndex, None, "script.netcommand.SetServerState", iState)