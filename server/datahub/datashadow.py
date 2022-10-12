# coding:utf-8

from datahub.mysql.mysqlbase import CMysqlBase

class CDataShadow(CMysqlBase):
	pass

class CPlayerDataShadow(CDataShadow):
	m_Type = "player"
	m_TblName = "tbl_player"
	m_ColName = ["data"]