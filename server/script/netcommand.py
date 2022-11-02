# -*- coding: utf-8 -*-
from mylog.logcmd import PrintWarning
from protocol import *
from pubdefines import CallManagerFunc, APPID, SECRETKEY

import script.login.net as ln
import script.login.login as login
import netpackage as np
import conf
import script.player as player
import script.gm.excutor as gm
import script.common as common

RPC_PROTOCOL = [SS_RPCRESPONSE, SS_RPCCALL, SS_RESPONSEERR]

GPS_PROTOCOL_COMMAND = {
	C2S_GMORDER: gm.ExecGMOrder,
	C2S_TOASTCB: common.TipAnswer,
	C2S_MODALCB: common.TipAnswer,

}

if "g_ServerState" not in globals():
	g_ServerState = 0		#0-不允许登录, 1-允许权限账号登录, 2-允许全部账号登录

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
	global g_ServerState
	iConnectID, data = tData
	oNetPackage = np.UnpackPrepare(data)
	iDataHeader = np.UnpackInt16(oNetPackage)
	if 0x100 <= iDataHeader < 0x1000:
		#所有服务器都有可能接收到rpc协议
		if iDataHeader in RPC_PROTOCOL:
			import rpc.myrpc as rpc
			data = np.UnpackEnd(oNetPackage)
			rpc.Receive(iDataHeader, data)
	elif iDataHeader >= 0x1000:
		#客户端协议只会在GATE接收
		if not g_ServerState and iDataHeader != CS_HELLO:
			return
		if iDataHeader not in REGIST:
			PrintWarning("protocol %s not registed"%iDataHeader)
			return
		if iDataHeader in GATEHANDLE:
			if GateHandle(iConnectID, iDataHeader):
				return
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
		sOpenID = np.UnpackS(oNetPackage)
		login.Login(iConnectID, sOpenID)
		return

	sOpenid = player.GetOpenIDByConnectID(iConnectID)
	who = player.GetOnlinePlayer(sOpenid)
	if not who or getattr(who, "m_OffLine", 0):
		PrintWarning("%s is in offline but receive protocol"%who)
		return
	global GPS_PROTOCOL_COMMAND
	func = GPS_PROTOCOL_COMMAND.get(iDataHeader, None)
	if func:
		func(who, oNetPackage)

def GateHandle(iConnectID, iDataHeader):
	if not conf.IsGate():
		PrintWarning("client connect to not gate server ! ")
		return 1
	if iDataHeader == CS_HELLO:
		SendHello(iConnectID)
		return 1
	elif iDataHeader == CS_GETAPPFLAG:
		SendAppKey(iConnectID)
		return 1
	elif iDataHeader == C2S_GMORDER:
		# GM指令检查筛选
		return 0
	return 1

def SendHello(iConnectID):
	global g_ServerState
	oNetPack = np.PacketPrepare(CS_HELLO)
	np.PacketAddInt8(g_ServerState, oNetPack)
	np.PacketSend(iConnectID, oNetPack)

def SendAppKey(iConnectID):
	oNetPack = np.PacketPrepare(CS_GETAPPFLAG)
	np.PacketAddS(APPID, oNetPack)
	np.PacketAddS(SECRETKEY, oNetPack)
	np.PacketSend(iConnectID, oNetPack)

def SetServerState(oResponse, iState):
	"""
	在GATE执行
	"""
	global g_ServerState
	PrintNotify("GATE set server state: %s"%iState)
	g_ServerState = iState
	oResponse(1)

def GetServerState(oResponse):
	"""
	在GATE执行
	"""
	global g_ServerState
	oResponse(g_ServerState)