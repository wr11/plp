# -*- coding: utf-8 -*-

import script.plp.datactl
import script.plp.operatemanager

def Init():
	script.plp.datactl.Init()
	script.plp.operatemanager.Init()
	PrintNotify("Plp Inited")