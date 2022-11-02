# coding:utf-8

from datahub.mysql.mysqlbase import CMysqlBase, MYSQL_INSERT, MYSQL_UPDATE, MYSQL_SELECT, MYSQL_MANUAL
from msgpack import packb, unpackb

class CDataTableShadow(CMysqlBase):
	"""
	代表 mysql中的一个表，一次存取多条记录的数据
	"""

	def __init__(self, sType, sTblName, lstColName):
		super(CDataTableShadow, self).__init__(sType, sTblName, lstColName)
		self.m_ListData = []

	def SetData(self, lstData):
		self.m_ListData = lstData

	def SaveToDataBase(self):
		lstArgs = []
		lstStrVal = []
		for dSaveData in self.m_ListData:
			dData = self.RepairData(dSaveData)
			primarydata = self.GetPrimaryData(dData)
			if not self.CheckPrimaryData(primarydata):
				PrintWarning("%s %s primarydata: %s is not illegal"%(self.m_Type, self.m_TblName, primarydata))
				continue
			lstArgs.append(primarydata)
			lstArgs.append(packb(dData))
			lstStrVal.append("(%s,%s)")
		sStrVal = ",".join(lstStrVal)
		sSqlStatement = "INSERT INTO %s VALUES %s"%(self.m_TblName, sStrVal)
		try:
			self.Handler(MYSQL_MANUAL, *lstArgs, Statement = sSqlStatement)
		except Exception as e:
			PrintWarning("ListData save failed!")
			PrintError(e)
			return

		self.m_ListData = []

	def RepairData(self, dData):
		#有需要时重写，可以用来线上修正数据
		return dData

	def CheckPrimaryData(self, primarydata):
		iCheck = 0
		sCheck = ""
		if type(iCheck) == type(primarydata):
			if primarydata > iCheck:
				return True
		elif type(sCheck) == type(primarydata):
			if primarydata != sCheck:
				return True
		else:
			return False
		return False

	def GetPrimaryData(self, dData):
		#获取主键("id")的值, 只可以为大于零整数，或者不为空的字符串, 不可与现有表中存在的主键值重复
		#need overwrite
		pass

	def LookUp(self, sSelectType, filter = None):
		if not filter:
			sStatement = "SELECT %s FROM %s"%(sSelectType ,self.m_TblName)
			ret = self.Handler(MYSQL_MANUAL, Statement = sStatement)
		else:
			sStatement = "SELECT %s FROM %s WHERE %s IN %s"%(sSelectType ,self.m_TblName, self.m_ColName[0], "%s")
			ret = self.Handler(MYSQL_MANUAL, filter, Statement = sStatement)

		if ret:
			for dResult in ret:
				if self.m_ColName[1] in dResult:
					bData = dResult[self.m_ColName[1]]
					unpack = unpackb(bData)
					dResult[self.m_ColName[1]] = unpack
		return ret

class CDataShadow(CMysqlBase):
	"""
	代表 mysql表中的某一个记录，一次只存取该条记录的数据
	"""

	def __init__(self, sType, sTblName, lstColName, sPrimary):
		super(CDataShadow, self).__init__(sType, sTblName, lstColName)
		self.m_PrimaryData = sPrimary

	def SetAttr(self, lstAttr):
		for sAttr in lstAttr:
			setattr(self, sAttr, None)
		self.m_SaveAttr = lstAttr

	def SaveToDataBase(self):
		data = self.Save()
		bData = packb(data)
		self.Handler(MYSQL_INSERT, self.m_PrimaryData, bData)

	def UpdateDataBase(self):
		data = self.Save()
		bData = packb(data)
		self.Handler(MYSQL_UPDATE, bData, self.m_PrimaryData)

	def LoadDataFromDataBase(self):
		lstData = self.Handler(MYSQL_SELECT, self.m_PrimaryData)
		if not lstData:
			return {}
		sData = lstData[0]["data"]
		data = unpackb(sData)
		self.Load(data)
		return data

	def Save(self):
		data = {}
		for sAttr in self.m_SaveAttr:
			if hasattr(self, sAttr):
				data[sAttr] = getattr(self, sAttr)
		return data

	def Load(self, data):
		if not data:
			return
		for sAttr, val in data.items():
			setattr(self, sAttr, val)

	def Update(self, data):
		if not data:
			return
		for sAttr, playerdata in data.items():
			setattr(self, sAttr, playerdata)
		self.UpdateDataBase()

#用户数据影子对象
if "g_PlayerShadowList" not in globals():
	g_PlayerShadowList = {}

def CreatePlayerDataShadow(sOpenID, lstAttr):
	oShadow = GetPlayerShadowByOpenID(sOpenID)
	if oShadow:
		return oShadow
	oShadow = CPlayerDataShadow(sOpenID)
	g_PlayerShadowList[sOpenID] = oShadow
	oShadow.SetAttr(lstAttr)
	return oShadow

def RemovePlayerDataShadow(oResponse, sOpenID):
	if not GetPlayerShadowByOpenID(sOpenID):
		return
	del g_PlayerShadowList[sOpenID]

def GetPlayerShadowByOpenID(sOpenID):
	return g_PlayerShadowList.get(sOpenID, None)

class CPlayerDataShadow(CDataShadow):

	def __init__(self, sOpenID):
		super(CPlayerDataShadow, self).__init__("player", "tbl_player", ["openid", "data",], sOpenID)
		self.m_OpenID = sOpenID

# Game Shadow
if "g_GameShadowList" not in globals():
	g_GameShadowList = {}

def CreateGameShadow(sGameName, lstAttr):
	oOldShadow = GetGameShadowByGameName(sGameName)
	if oOldShadow:
		return oOldShadow
	oShadow = CGameCtlShadow(sGameName)
	oShadow.SetAttr(lstAttr)
	g_GameShadowList[sGameName] = oShadow
	return oShadow

def GetGameShadowByGameName(sGameName):
	return g_GameShadowList.get(sGameName, None)

def RemoveGameShadow(sGameName):
	if not GetGameShadowByGameName(sGameName):
		return
	del g_GameShadowList[sGameName]

class CGameCtlShadow(CDataShadow):
	m_Type = "game"
	m_TblName = "tbl_game"
	m_ColName = ["game_name", "data",]

	def __init__(self, sGameName):
		super(CGameCtlShadow, self).__init__("game", "tbl_game", ["game_name", "data",], sGameName)
		self.m_GameName = sGameName


# listContainer shadow

if "g_ListContainerShadow" not in globals():
	g_ListContainerShadow = {}

def CreateListContainerShadow(sType):
	sTblName = sType
	o = GetListContainerShadowByType(sType)
	if o:
		return o
	oShadow = CListContainerShadow(sType, sTblName, ["plpid", "data",])
	g_ListContainerShadow[sType] = oShadow
	return oShadow

def GetListContainerShadowByType(sType):
	global g_ListContainerShadow
	return g_ListContainerShadow.get(sType, None)

def RemoveListContainer(sType):
	global g_ListContainerShadow
	if sType not in g_ListContainerShadow:
		return
	del g_ListContainerShadow[sType]

class CListContainerShadow(CDataTableShadow):

	def GetPrimaryData(self, dData):
		return dData["id"]