# -*- coding: utf-8 -*-
import onlinereload
onlinereload.Enable(onlinereload.blacklist)

from pubdefines import MSGQUEUE_SEND, MSGQUEUE_RECV, CallManagerFunc
from timer import Call_out

import mq
import script.netcommand as netcommand
import conf
import script.gameinit as gameinit
import script.link as link
import mylog

def RecvMq_Handler():
	iMax = conf.GetMaxReceiveNum()
	oRecvMq = mq.GetMq(MSGQUEUE_RECV)
	if oRecvMq.empty():
		Call_out(conf.GetInterval(), "RecvMq_Handler", RecvMq_Handler)
		return
	iHandled = 0
	while not oRecvMq.empty() and iHandled <= iMax:
		tData = oRecvMq.get()
		netcommand.MQMessage(tData)
	Call_out(conf.GetInterval(), "RecvMq_Handler", RecvMq_Handler)

def run(oSendMq, oRecvMq, oConfInitFunc):
	oConfInitFunc()
	mylog.Init("SCR")
	onlinereload.Init()
	link.Init()
	mq.SetMq(oSendMq, MSGQUEUE_SEND)
	mq.SetMq(oRecvMq, MSGQUEUE_RECV)
	Call_out(conf.GetInterval(), "RecvMq_Handler", RecvMq_Handler)
	Call_out(5, "CheckConnects", CheckConnects)

def CheckConnects():
	lstNeedConnects = conf.GetConnects()
	lstCheck = [(tConfig[0], tConfig[1]["iIndex"]) for tConfig in lstNeedConnects]
	lstLinks = CallManagerFunc("link", "Links")
	setUnConnected = set(lstCheck) - set(lstLinks)
	if not setUnConnected:
		gameinit.Init()
	else:
		PrintNotify("unconnect : %s"%(str(setUnConnected)))
		Call_out(5, "CheckConnects", CheckConnects)
