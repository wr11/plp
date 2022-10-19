# -*- coding: utf-8 -*-

#---------------mq----------------
MQ_LOCALMAKEROUTE = 0x1
MQ_DISCONNECT = 0x2
MQ_DATARECEIVED = 0x3
MQ_CLIENTCONNECT = 0x4
MQ_CLIENTDISCONNECT = 0x5

#---------------SS----------------
SS_RPCCALL = 0X100
SS_RPCRESPONSE = 0x101
SS_RESPONSEERR = 0x102
SS_IDENTIFY =  0x103

#---------------CS----------------
#客户端发起，需要服务端回调的共用一个协议号, 所有客户端与服务端协议都要加入regist中，gate据此拦截无效请求
#0x1500-0x1100为gameplay定制协议
C2S_GMORDER = 0x1000
CS_HELLO = 0x1001
CS_GETAPPFLAG = 0x1002
CS_LOGIN = 0x1003

# @plp start
C2S_SENDPLP = 0x1010
# @plp end

# @gameplay start
# @gameplay end

REGIST = [
	C2S_GMORDER, CS_HELLO, CS_GETAPPFLAG, CS_LOGIN, C2S_SENDPLP
]

GATEHANDLE = [
	CS_HELLO, CS_GETAPPFLAG
]