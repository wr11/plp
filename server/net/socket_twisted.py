# -*- coding: utf-8 -*-

from pubdefines import MSGQUEUE_SEND, MSGQUEUE_RECV, CLIENT, SERVER
from protocol import *
from netpackage import *

import twisted
import twisted.internet.protocol
import twisted.internet.reactor
import timer
import mq
import conf
import mylog
import hotfix

if "g_Connect" not in globals():
	g_Connect = {}

if "g_ClientConnect" not in globals():
	g_ClientConnect = {}

if "g_ClientConnectID" not in globals():
	g_ClientConnectID = 0

#-------------主动连接(作为客户端连接其他服务器)实例---------------
class DeferClient(twisted.internet.protocol.Protocol):

	def SetArgs(self, args):
		self.m_ServerID = args[0]
		self.m_Index = args[1]

	def connectionMade(self):
		global g_Connect
		sHost = self.transport.getPeer().host
		iPort = self.transport.getPeer().port
		tFlag = (sHost, iPort)
		if (tFlag not in g_Connect.keys()) or (tFlag in g_Connect.keys() and not g_Connect[tFlag].connected):
			g_Connect[tFlag] = self
			PrintNotify("%s %s  connected"%tFlag)
			if not timer.GetTimer("SendMq_Handler"):
				timer.Call_out(conf.GetInterval(), "SendMq_Handler", SendMq_Handler)

			PutData((MQ_LOCALMAKEROUTE, (sHost, iPort, self.m_ServerID, self.m_Index)))
		else:
			PrintWarning("connection repeated %s %s"%tFlag)
			self.transport.loseConnection()

	def dataReceived(self, data):
		# sHost = self.transport.getPeer().host
		# iPort = self.transport.getPeer().port
		# tFlag = (sHost, iPort)
		# PutData((C2S, tFlag, data))
		sHost = self.transport.getPeer().host
		iPort = self.transport.getPeer().port
		tFlag = (sHost, iPort)
		PrintError("wrong transform source%s %s"%tFlag)

	def connectionLost(self, reason):
		global g_Connect
		sHost = self.transport.getPeer().host
		iPort = self.transport.getPeer().port
		tFlag = (sHost, iPort)
		if tFlag in g_Connect:
			del g_Connect[tFlag]

		iServer = self.m_ServerID
		iIndex = self.m_Index
		tFlag1 = (iServer, iIndex)
		PutData((MQ_DISCONNECT, tFlag1))

		PrintNotify("disconnect %s %s"%(tFlag, reason))

class DefaultClientFactory(twisted.internet.protocol.ReconnectingClientFactory):
	protocol = DeferClient

	def __init__(self, *args):
		super().__init__()
		self.m_Args = args

	def buildProtocol(self, addr):
		assert self.protocol is not None
		p = self.protocol()
		p.factory = self
		p.SetArgs(self.m_Args)
		return p

#--------------接受连接(作为服务器接受其他客户端的连接)实例---------------
class CServer(twisted.internet.protocol.Protocol):
	def connectionMade(self):
		# global g_Connect
		# sHost = self.transport.getPeer().host
		# iPort = self.transport.getPeer().port
		# tFlag = (sHost, iPort)
		# if tFlag not in g_Connect.keys():
		# 	g_Connect[tFlag] = self
		# 	if not timer.GetTimer("SendMq_Handler"):
		# 		timer.Call_out(conf.GetInterval(), "SendMq_Handler", SendMq_Handler)
		# else:
		# 	self.transport.loseConnection()
		pass

	def connectionLost(self, reason):
		# global g_Connect
		# sHost = self.transport.getPeer().host
		# iPort = self.transport.getPeer().port
		# tFlag = (sHost, iPort)
		# if tFlag in g_Connect:
		# 	del g_Connect[tFlag]

		# PutData((SELF, MQ_DISCONNECT, tFlag))
		pass


	def dataReceived(self, data):
		sHost = self.transport.getPeer().host
		iPort = self.transport.getPeer().port
		tFlag = (sHost, iPort)
		PutData((MQ_DATARECEIVED, data))

class CBaseServerFactory(twisted.internet.protocol.Factory):
	protocol = CServer

#--------------客户端连接(作为服务器接受其他客户端的连接)实例---------------
class CClientServer(twisted.internet.protocol.Protocol):
	def connectionMade(self):
		global g_ClientConnect, g_ClientConnectID
		sHost = self.transport.getPeer().host
		iPort = self.transport.getPeer().port
		tFlag = (sHost, iPort)
		if (tFlag not in g_ClientConnect.keys()) or (tFlag in g_ClientConnect.keys() and not g_ClientConnect[tFlag].connected):
			g_ClientConnect[tFlag] = self
			PrintNotify("client %s %s connected"%tFlag)
			if not timer.GetTimer("SendMq_Handler"):
				timer.Call_out(conf.GetInterval(), "SendMq_Handler", SendMq_Handler)

			self.m_ClientConnectID = g_ClientConnectID
			PutData((MQ_CLIENTCONNECT, (sHost, iPort, g_ClientConnectID)))
			g_ClientConnectID += 1
		else:
			self.transport.loseConnection()

	def connectionLost(self, reason):
		iConnectID = self.m_ClientConnectID
		sHost = self.transport.getPeer().host
		iPort = self.transport.getPeer().port
		tFlag = (sHost, iPort)
		if tFlag in g_ClientConnect:
			del g_ClientConnect[tFlag]
		
		PutData((MQ_CLIENTDISCONNECT, (iConnectID,)))

		PrintNotify("client %s %s disconnected"%tFlag)


	def dataReceived(self, data):
		sHost = self.transport.getPeer().host
		iPort = self.transport.getPeer().port
		tFlag = (sHost, iPort)
		PrintNotify("client data received")
		PutData((MQ_DATARECEIVED, data))

class CClientServerFactory(twisted.internet.protocol.Factory):
	protocol = CClientServer


def run(oSendMq, oRecvMq, oConfInitFunc):
	global g_Connect
	oConfInitFunc()
	mylog.Init("NET")

	mq.SetMq(oSendMq, MSGQUEUE_SEND)
	mq.SetMq(oRecvMq, MSGQUEUE_RECV)

	lstConfigs = conf.GetConnects()
	lstLog = [(i[0], i[1]["iIndex"]) for i in lstConfigs]
	PrintNotify("need connect to %s"%str(lstLog))
	for tConfig in lstConfigs:
		iServerID, dConfig = tConfig
		sIP = dConfig["sIP"]
		iPort = dConfig["iPort"]
		index = dConfig["iIndex"]
		tFlag = (sIP, iPort)
		if tFlag in g_Connect:
			continue
		twisted.internet.reactor.connectTCP(sIP, iPort, DefaultClientFactory(iServerID, index))
	sMyIP, iMyPort = conf.GetCurProcessIPAndPort()
	twisted.internet.reactor.listenTCP(iMyPort, CBaseServerFactory())
	PrintNotify("open listen port %s ..."%iMyPort)
	if conf.IsGate():
		iClientPort = conf.GetClientPort()
		twisted.internet.reactor.listenTCP(iClientPort, CClientServerFactory())
		PrintNotify("open client listen port %s ..."%iClientPort)
	twisted.internet.reactor.run()

def SendMq_Handler():
	global g_Connect, g_ClientConnect
	iMax = conf.GetMaxSendNum()
	oMq = mq.GetMq(MSGQUEUE_SEND)
	if oMq.empty():
		timer.Call_out(conf.GetInterval(), "SendMq_Handler", SendMq_Handler)
		return
	iHandled = 0
	while not oMq.empty() and iHandled <= iMax:
		iHandled += 1
		tData = oMq.get()
		iTargetType, tFlag, bData = tData
		if iTargetType == SERVER:
			oProto = g_Connect.get(tFlag, None)
		elif iTargetType == CLIENT:
			oProto = g_ClientConnect.get(tFlag, None)
		else:
			oProto = None
		if oProto:
			oProto.transport.getHandle().sendall(bData)
		else:
			PrintWarning("No connect %s %s"%tFlag)
	timer.Call_out(conf.GetInterval(), "SendMq_Handler", SendMq_Handler)

def PutData(data):
	oRecvMq = mq.GetMq(MSGQUEUE_RECV)
	if oRecvMq:
		if oRecvMq.full():
			PrintWarning("data is loading")
			return
		oRecvMq.put(data)