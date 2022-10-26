# -*- coding: utf-8 -*-

from protocol import *
from netpackage import PacketPrepare, PacketAddInt16, PacketAddS, PacketSend, PacketAddBool, UnpackInt8, UnpackBool, UnpackS

import script.player as player

def S2CShowToast(sOpenID, sDesc, sIcon, sMsg, iDuration=1500, bMask = False, bNeedCallBack = False):
	"""
	sIcon:	  string, 图标(success, error, loading, none)
	sMsg:	   string, 提示信息
	iDuration:  int, 延迟时间(ms), 默认1500, 最大65535
	bMask:	  bool, 是否显示透明蒙层，防止触摸穿透，默认False
	bNeedCallBack: bool, 调用成功后回调函数
	"""
	oNetPack = PacketPrepare(S2C_SHOWTOAST)
	PacketAddS(sDesc, oNetPack)
	PacketAddS(sIcon, oNetPack)
	PacketAddS(sMsg, oNetPack)
	PacketAddInt16(iDuration, oNetPack)
	PacketAddBool(bMask, oNetPack)
	PacketAddBool(bNeedCallBack, oNetPack)
	PacketSend(sOpenID, oNetPack)

def S2CShowModal(sOpenID, sDesc, sTitle, sContent, sConfirmText = "确定", sConfirmColor = "#576B95", 
		bShowCancel = True, sCancelText = "取消", sCancelColor = "#000000",
		bEditable = False, sPlaceholderText = "提示", bNeedCallBack = True
	):
	"""
	sTitle: string, 提示标题
	sContent: string, 提示内容
	sConfirmText: string, 确定按钮显示文本，默认 "确定"
	sConfirmColor: string, 确认按钮的文字颜色，必须是 16 进制格式的颜色字符串, 默认 "#576B95"
	bShowCancel: bool, 是否显示取消按钮， 默认 True
	sCancelText: string, 取消按钮显示文本, 默认 "取消"
	sCancelColor: string, 取消按钮的文字颜色，必须是 16 进制格式的颜色字符串, 默认 "#000000"
	bEditable: bool, 是否显示输入框, 默认 False
	sPlaceholderText: string, 输入框提示文本, 默认 "提示"
	bNeedCallBack: bool, 是否需要回调, 默认 True
	"""
	oNetPack = PacketPrepare(S2C_SHOWMODAL)
	PacketAddS(sDesc, oNetPack)
	PacketAddS(sTitle, oNetPack)
	PacketAddS(sContent, oNetPack)
	PacketAddS(sConfirmText, oNetPack)
	PacketAddS(sConfirmColor, oNetPack)
	PacketAddBool(bShowCancel, oNetPack)
	PacketAddS(sCancelText, oNetPack)
	PacketAddS(sCancelColor, oNetPack)
	PacketAddBool(bEditable, oNetPack)
	PacketAddS(sPlaceholderText, oNetPack)
	PacketAddBool(bNeedCallBack, oNetPack)
	PacketSend(sOpenID, oNetPack)

def OpenTips(sOpenID, iType, sDesc, *args, **kwargs):
	"""
	iType: 1-toast 2-modal
	sDesc: 描述，用于回调(英文，唯一)，如果不需要回调，则可以传空字符串即可
	如果需要回调, 则使用callback传入回调函数, 默认需要回调
	"""
	who = player.GetOnlinePlayer(sOpenID)
	if not who:
		return
	if not hasattr(who, "_TipAnswer"):
		who._TipAnswer = {}
	dFunc = who._TipAnswer
	if sDesc in dFunc:
		PrintError("cannot open repeat tips %s"%sDesc)
		return
	bNeedCallBack = kwargs.get("bNeedCallBack", True)
	if "callback" in kwargs and bNeedCallBack:
		cbfunc = kwargs.pop("callback")
		if cbfunc:
			who._TipAnswer[sDesc] = cbfunc
	if iType == 1:
		S2CShowToast(sOpenID, sDesc, *args, **kwargs)
	elif iType == 2:
		S2CShowModal(sOpenID, sDesc, *args, **kwargs)

def TipAnswer(who, oNetPack):
	iType = UnpackInt8(oNetPack)
	sDesc = UnpackS(oNetPack)
	dFunc = getattr(who, "_TipAnswer", {})
	if not dFunc:
		return
	func = dFunc.get(sDesc, None)
	if not func:
		return
	del dFunc[sDesc]
	who._TipAnswer = dFunc
	if iType == 1:
		func(who)
	elif iType == 2:
		sContent = UnpackS(oNetPack)
		bComfirm = UnpackBool(oNetPack)
		bCancel = UnpackBool(oNetPack)
		func(who, sContent, bComfirm, bCancel)
