# -*- coding: utf-8 -*-
from io import BytesIO
from script.netcommand import g_ServerNum2Link
from protocol import *
from pubtool import CTimeOutManager
from timer import *
from myutil.mycorotine import Future

import mq
import pubdefines
import struct
import random
import msgpack
import traceback
import importlib
import netpackage as np
import conf

if "_g_FuncCache" not in globals():
	_g_FuncCache = {}
 
if "g_RPCManager" not in globals():
	g_RPCManager = {}
 
MAX_TIME_OUT = 3600

def GetGlobalFuncByName(sFunc):
	global _g_FuncCache
	func = _g_FuncCache.get(sFunc, None)
	if not func:
		lstPath = sFunc.split(".")
		if len(lstPath) < 2:
			func = None
		else:
			sMod = ".".join(lstPath[:-1])
			sName = lstPath[-1]
			obj = importlib.import_module(sMod)
			func = getattr(obj, sName)
		if not func:
			raise Exception("Erro Global Func Name %s"%sFunc)
		else:
			_g_FuncCache[sFunc] = func
	return func

class CCallBackFunctor:
	def __init__(self, oCBFunc, oTimeoutFunc, args, kwargs):
		self.m_Timeout = 3600
		self.m_TimeoutFunc = oTimeoutFunc
		self.m_CBFunc = oCBFunc
		self.m_args = args
		self.m_kwargs = kwargs
		self.m_Called = 0
  
	def __repr__(self):
		return "<rpc callback %s>"%self.m_CBFunc

	def SetTimeout(self, iTime):
		if iTime > MAX_TIME_OUT or iTime < 1:
			iTime = min(max(1, iTime), MAX_TIME_OUT)
		self.m_Timeout = iTime
  
	def ExecCallBack(self, args, kwargs):
		if not self.m_CBFunc:
			return
		if self.m_Called:
			return
		self.m_Called = 1
		callkwargs = self.m_kwargs.copy()
		callkwargs.update(kwargs)
		callargs = list(self.m_args) + args
		try:
			func = self.m_CBFunc
			self.m_CBFunc = None
			self.m_TimeoutFunc = None
			func(*callargs, **callkwargs)
		except:
			raise Exception("rpc回调函数执行错误%s"%(self.m_CBFunc))

	def ExecTimeout(self):
		if not self.m_TimeoutFunc:
			return
		if self.m_Called:
			return
		self.m_Called = 1
		try:
			func = self.m_TimeoutFunc
			self.m_CBFunc = None
			self.m_TimeoutFunc = None
			func(*self.m_args, **self.m_kwargs)
		except:
			raise Exception("rpc超时回调函数执行错误%s"%(self.m_TimeoutFunc))

	def ExecErr(self):
		PrintError("rpc remote error%s"%(self.m_CBFunc))
  
class CCallBackFunctor2:
	def __init__(self, oCBFunc):
		self.m_Timeout = 3600
		self.m_CBFunc = oCBFunc
		self.m_Called = 0
  
	def __repr__(self):
		return "<rpc callback %s>"%self.m_CBFunc

	def SetTimeout(self, iTime):
		if iTime > MAX_TIME_OUT or iTime < 1:
			iTime = min(max(1, iTime), MAX_TIME_OUT)
		self.m_Timeout = iTime
  
	def ExecCallBack(self, args, kwargs):
		if not self.m_CBFunc:
			return
		if self.m_Called:
			return
		self.m_Called = 1
		result = CResult(args, kwargs)
		try:
			func = self.m_CBFunc
			self.m_CBFunc = None
			func(result)
		except:
			raise Exception("rpc回调函数执行错误%s"%(self.m_CBFunc))

	def ExecTimeout(self):
		if not self.m_CBFunc:
			return
		if self.m_Called:
			return
		self.m_Called = 1
		result = CResult()
		result.SetTimeout()
		try:
			func = self.m_CBFunc
			self.m_CBFunc = None
			func(result)
		except:
			raise Exception("rpc回调函数执行错误%s"%(self.m_CBFunc))

	def ExecErr(self):
		if not self.m_CBFunc:
			return
		if self.m_Called:
			return
		self.m_Called = 1
		result = CResult()
		result.SetRunError()
		try:
			func = self.m_CBFunc
			self.m_CBFunc = None
			func(result)
		except:
			raise Exception("rpc回调函数执行错误%s"%(self.m_CBFunc))
  
class CResult(object):
	_E_TIMEOUT = "timeout"
	_E_RUNERR = "runerr"
 
	def __init__(self, args=None, kwargs=None):
		self.m_Args = args
		self.m_Kwargs = kwargs
		self.m_Error = None
		self.m_ErrorInfo = Exception()
  
	def SetTimeout(self):
		self.m_Error = self._E_TIMEOUT
		self.m_ErrorInfo = Exception("timeout")
  
	def SetRunError(self, err = "rpc remote err"):
		self.m_Error = self._E_RUNERR
		self.m_ErrorInfo = err

	def GetData(self, key=None):
		if self.m_Error is not None:
			raise Exception("response is err %s"%self.m_ErrorMsg())
		if not key:# 默认返回所有列表参数
			assert self.m_Args, "reponse has no args"
			if len(self.m_Args) == 1:
				return self.m_Args[0]
			return self.m_Args
		assert 0, "默认关闭字典型参数，没太大必要，直接打包字典返回即可"
		return self.m_Kwargs[key]

	def IsError(self):
		return self.m_Error is not None

	def IsTimeout(self):
		return self.m_Error == self._E_TIMEOUT

	def IsRunError(self):
		return self.m_Error == self._E_RUNERR

	def ErrorMsg(self):
		return self.m_ErrorInfo

class CRPC:
	def __init__(self):
		self.m_Packet = None
		self.m_CallBackBuff = CTimeOutManager()
		self.m_CBIdx = -1
		self._CheckTimeOut()
  
	def _CheckTimeOut(self):
		Call_out(5, "_CheckTimeOut", self._CheckTimeOut)
		lst = self.m_CallBackBuff.PopTimeOut()
		if lst:
			for oTask in lst:
				oTask.ExecTimeout()

	def InitCall(self, oCallBack, oPacket, sFunc, *args, **kwargs):
		self.m_Packet = oPacket
		idx = 0
		if oCallBack:
			idx = self._GetCallBackIdx()
			self._AddCallBack(idx, oCallBack)
		iServer, iIndex = conf.GetServerNum(), conf.GetProcessIndex()
		self.m_Packet._PushCallPacket((iServer, iIndex, sFunc, idx, args, kwargs))
		return idx

	def CallFunc(self, iServer, iIndex):
		oPack = np.PacketPrepare(SS_RPCCALL)
		np.PacketAddB(self.m_Packet.m_Data, oPack)
		np.S2SPacketSend(iServer, iIndex, oPack)

	def _GetCallBackIdx(self):
		if self.m_CBIdx == -1:
			self.m_CBIdx = random.randint(1,0xfffffff)
		self.m_CBIdx += 1
		if self.m_CBIdx >= 0x7fffffff:
			self.m_CBIdx = 1
		return self.m_CBIdx

	def _AddCallBack(self, idx, oCallBack):
		self.m_CallBackBuff.Push(idx, oCallBack.m_Timeout, oCallBack)

class CRPCPacket:
	def __init__(self):
		self.m_Data = None

	def _PushCallPacket(self, lstInfo):
		"""
		lstInfo 格式：
		iServerNum: 源服务器编号
		sFunc: 远程调用函数名
		CBIdx: 回调函数编号
		args: 列表参数
		kwargs: 字典参数
		"""
		global CMD_CALL
		oBuffer = BytesIO()
		for oParam in lstInfo:
			oBuffer.write(msgpack.packb(oParam, use_bin_type=True))
		self.m_Data = oBuffer.getvalue()

class CRPCResponse:
	def __init__(self, lstInfo):
		self.m_Called = 0
		self.m_SourceServer = (lstInfo[0], lstInfo[1])
		self.m_CallFunc = lstInfo[2]
		self.m_CBIdx = lstInfo[3]
		self.m_Args = lstInfo[4]
		self.m_Kwargs = lstInfo[5]

	def __repr__(self) -> str:
		return "< CRPCResponse ss:%s func:%s CB:%s args:%s kwargs%s>"% \
				(self.m_SourceServer, self.m_CallFunc, self.m_CBIdx, self.m_Args, self.m_Kwargs)

	def __call__(self, *args, **kwargs):
		if not self.m_CBIdx:		#不需要回调
			PrintWarning("do not need callback")
			return
		if self.m_Called:		#不可重复回调
			return
		self.m_Called = 1
		oPacket = CRPCPacket()
		iCurServer, iCurProcessIndex = conf.GetServerNum(), conf.GetProcessIndex()
		oPacket._PushCallPacket((iCurServer, iCurProcessIndex, self.m_CBIdx, args, kwargs))
		oPack = np.PacketPrepare(SS_RPCRESPONSE)
		np.PacketAddB(oPacket.m_Data, oPack)
		np.S2SPacketSend(self.m_SourceServer[0], self.m_SourceServer[1], oPack)

	def RemoteExcute(self):
		func = GetGlobalFuncByName(self.m_CallFunc)
		try:
			func(self, *self.m_Args, **self.m_Kwargs)
		except Exception as e:
			oPacket = CRPCPacket()
			iCurServer, iCurProcessIndex = conf.GetServerNum(), conf.GetProcessIndex()
			oPacket._PushCallPacket((iCurServer, iCurProcessIndex, self.m_CBIdx))
			oPack = np.PacketPrepare(SS_RESPONSEERR)
			np.PacketAddB(oPacket.m_Data, oPack)
			np.S2SPacketSend(self.m_SourceServer[0], self.m_SourceServer[1], oPack)
			PrintError(e)

def RemoteCallFunc(iServer, iIndex, oCallBack, sFunc, *args, **kwargs):
	tFlag = (iServer, iIndex)
	PrintNotify("remote call func start ...%s %s"%(iServer, iIndex))
	oRpc = GetRpcObject(tFlag)
	tLink = pubdefines.CallManagerFunc("link", "GetLink", tFlag[0], tFlag[1])
	oPacket = CRPCPacket()
	oRpc.InitCall(oCallBack, oPacket, sFunc, *args, **kwargs)
	oRpc.CallFunc(iServer, iIndex)
 
def GetRpcObject(tFlag):
	global g_RPCManager
	tLink = pubdefines.CallManagerFunc("link", "GetLink", tFlag[0], tFlag[1])
	if not tLink:
		PrintWarning("RPC %s %s not connected"%tFlag)
		return
	if tFlag not in g_RPCManager:
		g_RPCManager[tFlag] = CRPC()
	return g_RPCManager[tFlag]

def Receive(iHeader, data):
	oBuffer = BytesIO(data)
	unpacker = msgpack.Unpacker(oBuffer, raw=False)
	lstInfo = [unpacked for unpacked in unpacker]
	PrintNotify("rpc remote receive %s"%str(lstInfo))
	if iHeader == SS_RPCCALL:
		oResponse = CRPCResponse(lstInfo)
		oResponse.RemoteExcute()
	elif iHeader == SS_RPCRESPONSE:
		_OnResponse(lstInfo)
	elif iHeader == SS_RESPONSEERR:
		_OnResponseErr(lstInfo)
  
def _OnResponseErr(lstInfo):
	global g_RPCManager
	oRpc = g_RPCManager.get((lstInfo[0], lstInfo[1]))
	if not oRpc:
		PrintWarning("err rpc object has unload%s"%lstInfo[0])
		return
	oCallBack = oRpc.m_CallBackBuff.Get(lstInfo[2])
	if not oCallBack:
		PrintWarning("err rpccallback object has deleted%s"%lstInfo[2])
		return
	oCallBack.ExecErr()

def _OnResponse(lstInfo):
	global g_RPCManager
	tFlag = (lstInfo[0], lstInfo[1])
	oRpc = g_RPCManager.get(tFlag, 0)
	if not oRpc:
		PrintWarning("rpc object has unload%s %s"%tFlag)
		return
	oCallBack = oRpc.m_CallBackBuff.Get(lstInfo[2])
	if not oCallBack:
		PrintWarning("rpccallback object has deleted%s"%lstInfo[2])
		return
	oCallBack.ExecCallBack(lstInfo[3], lstInfo[4])
	oRpc.m_CallBackBuff.Pop(lstInfo[2])
	if oRpc.m_CallBackBuff.IsEmpty():
		del oRpc
		del g_RPCManager[tFlag]
 
def RpcFunctor(oCBFunc, oTimeoutFunc, *args, **kwargs):
	return CCallBackFunctor(oCBFunc, oTimeoutFunc, args, kwargs)

def RpcOnlyCBFunctor(oCBFunc, *args, **kwargs):
	return CCallBackFunctor(oCBFunc, None, args, kwargs)


#-------------------corotine-----------------
def AsyncRpcFunctor(oCBFunc):
	return CCallBackFunctor2(oCBFunc)

def AsyncRemoteCallFunc(iServer, iIndex, sFunc, *args, **kwargs):
	return _BaseBlockCall(iServer, iIndex, sFunc, args, kwargs)

def _BaseBlockCall(iServer, iIndex, sTatgetFunc, args, kwargs):
	tFlag = (iServer, iIndex)
	def _func(result):
		if not result.IsError():
			oFuture.set_result(result.GetData())
		elif result.IsTimeout():
			oFuture.set_exc_info(RpcTimeout("%s timeout"%sTatgetFunc))
		else:
			errmsg = result.ErrorMsg()
			oFuture.set_exc_info(RpcRunError(errmsg))

	oFuture = Future()
	cb = AsyncRpcFunctor(_func)
	iTimeOut = kwargs.pop("_timeout", None)
	if iTimeOut:
		cb.SetTimeout(iTimeOut)
	oRpc = GetRpcObject(tFlag)
	tLink = pubdefines.CallManagerFunc("link", "GetLink", tFlag[0], tFlag[1])
	oPacket = CRPCPacket()
	oRpc.InitCall(cb, oPacket, sTatgetFunc, *args, **kwargs)
	oRpc.CallFunc(iServer, iIndex)

class RpcException(Exception):
	pass

class RpcTimeout(RpcException):
	pass

class RpcRunError(RpcException):
	def __init__(self, e):
		self.m_RemoteExcp = e
		super(RpcRunError, self).__init__(e)
  
	def GetRemoteException(self):
		return self.m_RemoteExcp