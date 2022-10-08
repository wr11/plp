# -*- coding: utf-8 -*-
from pubdefines import MSGQUEUE_SEND, MSGQUEUE_RECV
from timer import Call_out

import mq
import script.netcommand as netcommand
import script.user as user
import script.link as link
import conf
import mylog
import hotfix

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
	hotfix.Init()
	user.Init()
	link.Init()
	mq.SetMq(oSendMq, MSGQUEUE_SEND)
	mq.SetMq(oRecvMq, MSGQUEUE_RECV)
	Call_out(conf.GetInterval(), "RecvMq_Handler", RecvMq_Handler)