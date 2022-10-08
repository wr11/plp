# -*- coding: utf-8 -*-
import mylog.logcmd as logcmd
import mylog.logfile as logfile

def Init(sThread):
	logcmd.Init(sThread)
	logfile.Init(sThread)