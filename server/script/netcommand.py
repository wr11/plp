# -*- coding: utf-8 -*-
from mylog.logcmd import PrintWarning
from protocol import *
from pubdefines import CallManagerFunc, APPID, SECRETKEY

import script.login.net as ln
import script.login.login as login
import netpackage as np
import conf
import script.player as player

RPC_PROTOCOL = [SS_RPCRESPONSE, SS_RPCCALL, SS_RESPONSEERR]

class CNetCommand:
	def __init__(self):
		self.m_Map = {
			C2S_GMORDER : ln.NetCommand
		}

	def CallCommand(self, iConnectID, iHeader, oNetPackage, who=None):
		func = self.m_Map.get(iHeader, None)
		if func:
			func(iConnectID, oNetPackage)

def MQMessage(tData):
	iMQProto, data = tData
	if iMQProto < 0x100:
		OnMQMessage(tData)
		return
	else:
		OnOtherMessage(data)

def OnMQMessage(tData):
	iMQHeader, data = tData
	ParseMQMessage(iMQHeader, data)

def OnOtherMessage(data):
	pass

def ParseMQMessage(iMQHeader, data):
	if iMQHeader == MQ_LOCALMAKEROUTE:
		sHost, iPort, iServer, iIndex = data
		CallManagerFunc("link", "AddLink", sHost, iPort, iServer, iIndex)
		PrintNotify("scr connected %s %s %s %s"%(sHost, iPort, iServer, iIndex))
	elif iMQHeader == MQ_DISCONNECT:
		iServer, iIndex = data
		CallManagerFunc("link", "DelLink", iServer, iIndex)
		PrintNotify("scr disconnected%s %s"%(iServer, iIndex))
	elif iMQHeader == MQ_CLIENTCONNECT:
		sHost, iPort, iConnectID = data
		CallManagerFunc("link", "AddClientLink", sHost, iPort, iConnectID)
	elif iMQHeader == MQ_CLIENTDISCONNECT:
		import rpc
		import conf
		iConnectID = data[0]
		CallManagerFunc("link", "DelClientLink", iConnectID)
		iServer, iIndex = conf.GetGPS()
		rpc.RemoteCallFunc(iServer, iIndex, None, "script.player.PlayerOffLine", iConnectID)
	elif iMQHeader == MQ_DATARECEIVED:
		OnNetCommand(data)

def OnNetCommand(tData):
	iConnectID, data = tData
	oNetPackage = np.UnpackPrepare(data)
	iDataHeader = np.UnpackInt16(oNetPackage)
	PrintNotify("receive header data %s" % iDataHeader)
	if 0x100 <= iDataHeader < 0x1000:
		#所有服务器都有可能接收到rpc协议
		if iDataHeader in RPC_PROTOCOL:
			import rpc.myrpc as rpc
			data = np.UnpackEnd(oNetPackage)
			rpc.Receive(iDataHeader, data)
	elif iDataHeader >= 0x1000:
		#客户端协议只会在GATE接收
		# CNetCommand().CallCommand(iDataHeader, oNetPackage)
		if iDataHeader in GATEHANDLE:
			GateHandle(iConnectID, iDataHeader)
		else:
			import rpc.myrpc as rpc
			import conf
			iServer, iIndex = conf.GetGPS()
			rpc.RemoteCallFunc(iServer, iIndex, None, "script.netcommand.GPSNetCommand", iConnectID, data)

def GPSNetCommand(oResPonse, iConnectID, data):
	if not conf.IsGPS():
		return
	oNetPackage = np.UnpackPrepare(data)
	iDataHeader = np.UnpackInt16(oNetPackage)
	if iDataHeader == CS_LOGIN:
		login.Login(iConnectID, oNetPackage)
	elif iDataHeader == C2S_GMORDER:
		sOrder = np.UnpackS(oNetPackage)
		PrintDebug(sOrder)
		exec(sOrder)
	else:
		pass

def GateHandle(iConnectID, iDataHeader):
	if not conf.IsGate():
		PrintWarning("client connect to not gate server ! ")
		return
	if iDataHeader == CS_HELLO:
		SendHello(iConnectID)
	elif iDataHeader == CS_GETAPPFLAG:
		SendAppKey(iConnectID)

def SendHello(iConnectID):
	oNetPack = np.PacketPrepare(CS_HELLO)
	np.PacketSend(iConnectID, oNetPack)

def SendAppKey(iConnectID):
	oNetPack = np.PacketPrepare(CS_GETAPPFLAG)
	np.PacketAddS(APPID, oNetPack)
	np.PacketAddS(SECRETKEY, oNetPack)
	np.PacketSend(iConnectID, oNetPack)