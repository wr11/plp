# -*- coding: utf-8 -*-

from myutil.mycorotine import coroutine, Return

import timer
import rpc
import conf


#List Container
if "g_ListContainer" not in globals():
	g_ListContainer = {}

def RegistListContainer(oContainer): #请勿重复注册
	global g_ListContainer
	sTypeName = oContainer.m_TypeName
	if sTypeName in g_ListContainer:
		PrintError("%s repeat regist listcontainer")
		return
	g_ListContainer[sTypeName] = oContainer

def Init():
	timer.Call_out(2 * 60, "listcontainer_save", SaveListContainer)

def SaveListContainer():
	global g_ListContainer
	data = {}
	for sTypeName, oContainer in g_ListContainer.items():
		lstData = oContainer.Save()
		if not lstData:
			continue
		data[sTypeName] = lstData
	iServer, iIndex = conf.GetDBS()
	rpc.RemoteCallFunc(iServer, iIndex, None, "datahub.manager.ListContainerSaveToDBS", data)

class CListContainer(list):
	"""
	对应CDataTableShadow，一个CListContainer用来描述一个表，列表中的每个对象对应表中一行记录
	"""

	m_TypeName = ""		#用于唯一标识，和数据库表名一样

	def Save(self):
		data = []
		for obj in self:
			data.append(obj.Save())
		self.clear()
		return data

	@coroutine
	def SelectDataFromDB(self, sSelectType):
		"""
		sSelectType 为select from之间的值，可以为*,max(字段名), min(字段名), sum(字段名), avg(字段名)以及具体字段名等合法值
		"""
		iServer, iIndex = conf.GetDBS()
		ret = yield rpc.AsyncRemoteCallFunc(iServer, iIndex, "datahub.manager.LoadDataFromTableShadow", self.m_TypeName, sSelectType)
		raise Return(ret)