# -*- coding: utf-8 -*-

import pymysql
import pymysql.cursors
import msgpack
import pubdefines
import timer

MYSQL_SELECT = 1
MYSQL_INSERT = 2
MYSQL_UPDATE = 3
MYSQL_MANUAL = 4
MYSQL_HANDLE_TYPE = [MYSQL_SELECT, MYSQL_INSERT, MYSQL_UPDATE, MYSQL_MANUAL]

class CMysqlConn:
	def __init__(self, sCursorType=pubdefines.MYSQL_DICTCURSOR):
		self.m_Config = {
			"host":'localhost',
			"user":'root',
			"password":'mytool2021',
			"db":'db_plp',
			"charset":'utf8',
			"cursorclass":eval("pymysql.cursors.%s" % sCursorType),
		}
		self.m_Conn = self.MakeConnection()

	def MakeConnection(self):
		conn = pymysql.connect(**self.m_Config)
		timer.Call_out(10*60, "CheckMysqlConnection", self.CheckConnection)
		return conn

	def GetConnection(self):
		return self.m_Conn

	def CheckConnection(self):
		self.m_Conn.ping(reconnect = True)

if "g_MysqlConn" not in globals():
	g_MysqlConn = CMysqlConn()

def GetMysqlConnect():
	return g_MysqlConn.GetConnection()

class CMysqlBase:

	"""
	m_ColName 必有data列，以及ID列（用于唯一主键，字符串类型，不用int），且顺序为[id, data]
	"""

	def __init__(self, sType, sTblName, lstColName = ["id", "data"]):
		self.m_Conn = GetMysqlConnect()
		self.m_Type = sType		#子类需对该属性重新赋值
		self.m_TblName = sTblName
		self.m_ColName = lstColName

	def __repr__(self):
		cls = self.__class__
		return "<%s %s(%d) at %s>" % (cls.__module__, cls.__name__, self.m_Type, self.m_State)

	def CheckConfig(self):
		assert self.m_Type and self.m_TblName, "mysqlbase config wrong"

	def GetPrimaryKey(self):
		return self.m_ColName[0]

	def GenerateSqlStatement(self, iType):
		if iType == MYSQL_SELECT:			#查询语句
			return "SELECT * FROM %s WHERE %s=%s;" % (self.m_TblName, self.GetPrimaryKey(), "%s")
		elif iType == MYSQL_INSERT:		#插入语句
			iLen = len(self.m_ColName)
			lstPos = ["%s"]*iLen
			sAll = ",".join(lstPos)
			return "INSERT INTO %s VALUES (%s);" % (self.m_TblName, sAll)
		elif iType == MYSQL_UPDATE:		#更新语句
			lstUpdateName = []
			lstColUpdate = self.m_ColName[1:]
			for sName in lstColUpdate:
				lstUpdateName.append("%s=%s"%(sName, "%s"))
			sUpdate = ",".join(lstUpdateName)
			return "UPDATE %s SET %s WHERE %s=%s;" % (self.m_TblName, sUpdate, self.GetPrimaryKey(), "%s")

	def Handler(self, iType, *args, **kwargs):
		"""
		kwargs param:
		Statement: 自定义语句

		args顺序
		select: where id=%s
		insert: values(%s, %s, ...)
		update: set id=%s,data=%s... WHERE id=%s
		"""
		self.CheckConfig()
		if iType not in MYSQL_HANDLE_TYPE:
			PrintError("数据库操作类型错误")
			return
		with self.m_Conn.cursor() as oCursor:
			if iType == MYSQL_MANUAL:
				sSqlState = kwargs.get("Statement")
			else:
				sSqlState = self.GenerateSqlStatement(iType)
			# PrintDebug(sSqlState)
			if not args:
				oCursor.execute(sSqlState)
			else:
				oCursor.execute(sSqlState, args)
			result = oCursor.fetchall()
		self.m_Conn.commit()
		PrintDebug("mysql handler",iType, result)
		return result

	#todo 需要支持其他游标类型的解析
	def ResultInterrupt(self, result):
		if self.m_CursorType == pubdefines.MYSQL_DICTCURSOR:
			pass
		elif self.m_CursorType == pubdefines.MYSQL_CURSOR:
			pass
		else:
			pass


	def LoadAll(self):
		self.CheckConfig()

	def SaveAll(self):
		self.CheckConfig()

	def Save(self):
		pass


#test
# class CTestSql(CMysqlBase):

# 	m_Type = "test"
# 	m_TblName = "test"


# def main():
# 	oTestMysql = CTestSql(pubdefines.MYSQL_DICTCURSOR, "test")
# 	oTestMysql.Handler(MYSQL_INSERT, SetValue = "id=15332342922,test=123")
# 	oTestMysql.Handler(MYSQL_SELECT, Filter = "test=123")
# 	oTestMysql.Handler(MYSQL_UPDATE, SetValue = "test=124", Filter = "test=123")
# 	result = oTestMysql.Handler(MYSQL_SELECT, Filter = "test=124")
# 	result=oTestMysql.Handler(MYSQL_MANUAL, Statement = "select id from %s"%oTestMysql.m_TblName)

# 	PrintDebug(result)