# -*- coding: utf-8 -*-

from myutil.mycorotine import coroutine, Return

import timer
import rpc
import conf

SAVE_LISTCONTAINER = 4

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
	timer.Call_out(SAVE_LISTCONTAINER, "listcontainer_save", SaveListContainer)

	PrintNotify("Containers Inited")

def SaveListContainer():
	global g_ListContainer
	data = {}
	for sTypeName, oContainer in g_ListContainer.items():
		lstData = oContainer.Save()
		if not lstData:
			continue
		data[sTypeName] = lstData
	# PrintDebug("======", data)
	if not data:
		timer.Call_out(SAVE_LISTCONTAINER, "listcontainer_save", SaveListContainer)
		return
	iServer, iIndex = conf.GetDBS()
	rpc.RemoteCallFunc(iServer, iIndex, None, "datahub.manager.ListContainerSaveToDBS", data)
	timer.Call_out(SAVE_LISTCONTAINER, "listcontainer_save", SaveListContainer)

@coroutine
def ShutDown():
	global g_ListContainer
	if timer.GetTimer("listcontainer_save"):
		timer.Remove_Call_out("listcontainer_save")
	data = {}
	for sTypeName, oContainer in g_ListContainer.items():
		lstData = oContainer.Save()
		if not lstData:
			continue
		data[sTypeName] = lstData
	if not data:
		raise Return(1)
	iServer, iIndex = conf.GetDBS()
	ret = yield rpc.AsyncRemoteCallFunc(iServer, iIndex, "datahub.manager.ListContainerSaveToDBS", data)
	raise Return(ret)
	

class CListContainer(list):
	"""
	对应CDataTableShadow，一个CListContainer用来描述一个表，列表中的每个对象对应表中一行记录
	"""

	m_TypeName = ""		#用于唯一标识，和数据库表名一样

	def __init__(self, *args, **kwargs):
		super(CListContainer, self).__init__(*args, **kwargs)
		self.m_KeyList = []

	def Append(self, key, val):
		self.m_KeyList.append(key)
		self.append(val)

	def GetItem(self, key):
		if key not in self.m_KeyList:
			return None
		iIndex = self.m_KeyList.index(key)
		return self[iIndex]

	def Remove(self, key):
		if key not in self.m_KeyList:
			return
		iIndex = self.m_KeyList.index(key)
		del self.m_KeyList[iIndex]
		del self[iIndex]

	def Keys(self):
		return self.m_KeyList

	def Items(self):
		return self

	def Clear(self):
		self.clear()
		self.m_KeyList.clear()

	def Save(self):
		data = []
		for obj in self:
			data.append(obj.Save())
		self.Clear()
		return data

	@coroutine
	def SelectSingleDataFromDB(self, sSelectType):
		"""
		sSelectType 为select from之间的值，可以为*,max(字段名/*), min(字段名/*), sum(字段名/*), avg(字段名/*), COUNT(字段名/*)以及具体字段名等合法值
		"""
		iServer, iIndex = conf.GetDBS()
		ret = yield rpc.AsyncRemoteCallFunc(iServer, iIndex, "datahub.manager.LoadDataFromTableShadow", self.m_TypeName, sSelectType)
		raise Return(ret)

	@coroutine
	def SelectMultiDataFromDB(self, sSelectType, lstPrimaryData):
		"""
		sSelectType 为select from之间的值，可以为*,max(字段名), min(字段名), sum(字段名), avg(字段名)以及具体字段名等合法值
		lstPrimaryData 为主键列表，用于where in做条件筛选
		"""
		lstNewPrimaryData = []
		lstKeys = self.Keys()
		data = {}
		for i in lstPrimaryData:
			if i not in lstKeys:
				lstNewPrimaryData.append(i)
			else:
				data[i] = self.GetItem(i)
		iServer, iIndex = conf.GetDBS()
		ret = yield rpc.AsyncRemoteCallFunc(iServer, iIndex, "datahub.manager.LoadMultiDataFromTableShadow", self.m_TypeName, sSelectType, lstNewPrimaryData)
		raise Return(ret)