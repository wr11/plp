# -*- coding: utf-8 -*-

from pubdefines import SERVER_DIR_ROOT

import conf
import timer

IGNORE_LIST = ["doc",]

def Init():
	if not conf.IsDebug() or not conf.IsAutoReloadOpen():
		InitReloadFile()
		return
	PrintNotify("auto reload inited")
	timer.Call_out(conf.GetAutoReloadInterval(), "AutoReload", MyAutoReload)

def InitReloadFile():
	try:
		import hotfix.reloadbox
	except Exception as e:
		PrintError("reload box is not ready!!")
		return
	PrintNotify("manul reload inited")
	timer.Call_out(conf.GetManulReloadInterval(), "ManulReload", ManulReload)

def ManulReload():
	import hotfix.reloadbox as reloadbox
	from importlib import reload, import_module
	oMod = reload(reloadbox)
	lstReloadFile = getattr(oMod, "FILE_LIST", [])
	if not lstReloadFile:
		timer.Call_out(conf.GetManulReloadInterval(), "ManulReload", ManulReload)
		return
	PrintNotify("manul reloading %s"%str(lstReloadFile))
	for sMod in lstReloadFile:
		obj = import_module(sMod)
		oNewModule = reload(obj)
		func = getattr(oNewModule, "OnReload", None)
		if func:
			func()
	timer.Call_out(conf.GetManulReloadInterval(), "ManulReload", ManulReload)

def MyAutoReload():
	LookFile(True, True)
	timer.Call_out(conf.GetAutoReloadInterval(), "AutoReload", MyAutoReload)

def LookFile(bReload = False, bNotifyNew = False):
	import os
	sCurPath = os.getcwd()
	sCurPath = "%s\%s"%(sCurPath, SERVER_DIR_ROOT)
	lstFile = os.listdir(sCurPath)
	for sName in lstFile:
		if sName in IGNORE_LIST:
			continue
		ReloadPyFile(sCurPath, sName, bReload, bNotifyNew)

def ReloadPyFile(sCurPath, sName, bReload, bNotifyNew):
	import sys
	if sName.endswith(".py"):
		if bReload:
			from importlib import reload, import_module
			lstMod = []
			sMod = sName.split(".")[0]
			iIndex = sCurPath.find(SERVER_DIR_ROOT)
			sPath = sCurPath[iIndex + len(SERVER_DIR_ROOT)+1:]
			if not sPath:
				lstPath = []
			else:
				lstPath = sPath.split("\\")
			if sMod not in  ("__init__",):
				lstPath.append(sMod)
			iLen = len(lstPath)
			for i in range(iLen):
				lstMod.append(".".join(lstPath[i:]))
			for sModName in lstMod:
				obj = import_module(sModName)
				oNewModule = reload(obj)
			func = getattr(oNewModule, "OnReload", None)
			if func:
				func()
	elif "." not in sName:
		import os
		sCurPath = sCurPath + "\%s"%sName
		sys.path.append(sCurPath)
		lstFile = os.listdir(sCurPath)
		for sFile in lstFile:
			ReloadPyFile(sCurPath, sFile, bReload, bNotifyNew)