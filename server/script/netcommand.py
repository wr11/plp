# -*- coding: utf-8 -*-
from protocol import *
from pubdefines import CallManagerFunc

import script.login.net as ln
import netpackage as np

RPC_PROTOCOL = [SS_RPCRESPONSE, SS_RPCCALL, SS_RESPONSEERR]

if "g_ServerNum2Link" not in globals():
	g_ServerNum2Link = {}

class CNetCommand:
	def __init__(self):
		self.m_Map = {
			C2S_GMORDER : ln.NetCommand
		}

	def CallCommand(self, iHeader, oNetPackage, who=None):
		func = self.m_Map.get(iHeader, None)
		if func:
			func(who, oNetPackage)

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
		iConnectID = data[0]
		CallManagerFunc("link", "DelClientLink", iConnectID)
	elif iMQHeader == MQ_DATARECEIVED:
		NetCommand(data)

def NetCommand(data):
	oNetPackage = np.UnpackPrepare(data)
	iDataHeader = np.UnpackI(oNetPackage)
	PrintNotify("receive header data %s" % iDataHeader)
	if 0x100 <= iDataHeader < 0x1000:
		if iDataHeader in RPC_PROTOCOL:
			import rpc.myrpc as rpc
			data = np.UnpackEnd(oNetPackage)
			rpc.Receive(iDataHeader, data)
	elif iDataHeader >= 0x1000:
		CNetCommand().CallCommand(iDataHeader, oNetPackage)