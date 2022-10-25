# coding:utf-8

from datahub.mysql.mysqlbase import CMysqlBase, MYSQL_INSERT, MYSQL_UPDATE, MYSQL_SELECT
from msgpack import packb, unpackb

class CDataShadow(CMysqlBase):

	def __init__(self, sPrimary):
		super().__init__()
		self.m_PrimaryData = sPrimary

	def SaveToDataBase(self):
		data = self.Save()
		bData = packb(data)
		self.Handler(MYSQL_INSERT, self.m_PrimaryData, bData)

	def UpdateDataBase(self):
		data = self.Save()
		bData = packb(data)
		self.Handler(MYSQL_UPDATE, self.m_PrimaryData, bData, self.m_PrimaryData)

	def LoadDataFromDataBase(self):
		lstData = self.Handler(MYSQL_SELECT, self.m_PrimaryData)
		if not lstData:
			return {}
		sData = lstData[0]["data"]
		data = unpackb(sData)
		self.Load(data)
		return data

	def Load(data):
		#need overwrite
		pass

	def Save():
		#need overwrite
		pass

	def Update():
		#need overwrite
		pass

if "g_PlayerShadowList" not in globals():
	g_PlayerShadowList = {}

#用户数据影子对象
def CreatePlayerDataShadow(sOpenID):
	oShadow = CPlayerDataShadow(sOpenID)
	g_PlayerShadowList[sOpenID] = oShadow
	return oShadow

def RemovePlayerDataShadow(oResponse, sOpenID):
	PrintDebug("RemovePlayerDataShadow", sOpenID)
	if not GetPlayerShadowByOpenID(sOpenID):
		return
	del g_PlayerShadowList[sOpenID]

def GetPlayerShadowByOpenID(sOpenID):
	return g_PlayerShadowList.get(sOpenID, None)

class CPlayerDataShadow(CDataShadow):
	m_Type = "player"
	m_TblName = "tbl_player"
	m_ColName = ["openid", "data",]

	def __init__(self, sOpenID):
		super(CPlayerDataShadow, self).__init__(sOpenID)
		self.m_OpenID = sOpenID
		self.m_SendedNum = 0
		self.m_SendedList = []

	def Save(self):
		data = {}
		data["SendNum"] = self.m_SendedNum
		data["SendedList"] = self.m_SendedList
		return data

	def Load(self, data):
		if not data:
			return
		self.m_SendedNum = data["SendNum"]
		self.m_SendedList = data["SendedList"]

	def Update(self, data):
		for sAttr, playerdata in data:
			setattr(self, sAttr, playerdata)
		self.UpdateDataBase()

# Game Shadow
if "g_GameShadowList" not in globals():
	g_GameShadowList = {}

def CreateGameShadow(sGameName):
	oOldShadow = GetGameShadowByGameName(sGameName)
	if oOldShadow:
		return oOldShadow
	oShadow = CGameCtlShadow(sGameName)
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
		super(CGameCtlShadow, self).__init__(sGameName)
		self.m_GameName = sGameName

	def Setattr(self, lstAttr):
		for sAttr in lstAttr:
			setattr(self, sAttr, None)
		self.m_SaveAttr = lstAttr

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
		for sAttr, playerdata in data:
			setattr(self, sAttr, playerdata)
		self.UpdateDataBase()


# plp shadow
class CPLPShadow(CDataShadow):
	m_Type = "plp"
	m_TblName = "tbl_plp"
	m_ColName = ["plpid", "data",]