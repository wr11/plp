# -*- coding: utf-8 -*-
"""
模块已废弃！！！！
"""
from pubdefines import SERVER_DIR_ROOT

import conf
import timer
import os

IGNORE_LIST = ["doc", "allocate",]

if os.name == "nt":
	DELIMITER = "\\"
else:
	DELIMITER = "/"

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
	timer.Call_out(conf.GetManualReloadInterval(), "ManulReload", ManulReload)

def ManulReload():
	import hotfix.reloadbox as reloadbox
	from importlib import reload, import_module
	oMod = reload(reloadbox)
	lstReloadFile = getattr(oMod, "MODULE_LIST", [])
	if not lstReloadFile:
		timer.Call_out(conf.GetManualReloadInterval(), "ManulReload", ManulReload)
		return
	PrintNotify("manul reloading %s"%str(lstReloadFile))
	for sMod in lstReloadFile:
		obj = import_module(sMod)
		oNewModule = reload(obj)
		func = getattr(oNewModule, "OnReload", None)
		if func:
			func()
	timer.Call_out(conf.GetManualReloadInterval(), "ManulReload", ManulReload)

def MyAutoReload():
	LookFile(True, True)
	timer.Call_out(conf.GetAutoReloadInterval(), "AutoReload", MyAutoReload)

def LookFile(bReload = False, bNotifyNew = False):
	import os
	sCurPath = os.getcwd()
	sCurPath = "%s%s%s"%(sCurPath, DELIMITER, SERVER_DIR_ROOT)
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
				lstPath = sPath.split(DELIMITER)
			if sMod not in  ("__init__",):
				lstPath.append(sMod)
			sModName = ".".join(lstPath)
			obj = None
			try:
				obj = import_module(sModName)
			except Exception as e:
				PrintError(e, sModName)
			if obj:
				try:
					oNewModule = reload(obj)
					func = getattr(oNewModule, "OnReload", None)
					if func:
						func()
				except Exception as e:
					PrintError(obj, e)
	elif "." not in sName:
		import os
		sCurPath = sCurPath + "%s%s"%(DELIMITER, sName)
		sys.path.append(sCurPath)
		lstFile = os.listdir(sCurPath)
		for sFile in lstFile:
			ReloadPyFile(sCurPath, sFile, bReload, bNotifyNew)