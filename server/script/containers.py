# -*- coding: utf-8 -*-

import timer

if "g_ListContainer" not in globals():
	g_ListContainer = []

def Regist(oContainer):
	global g_ListContainer
	g_ListContainer.append(oContainer)

def Init():
	timer.Call_out(60, "listcontainer_save", SaveListContainer)
	return

def SaveListContainer():
	return

class CListContainer(list):
	def Save(self):
		data = []
		for obj in self:
			data.append(obj.Save())
		self.clear()
		return data