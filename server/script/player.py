# -*- coding: utf-8 -*-

if "PLAYER_LIST" not in globals():
	PLAYER_LIST = {}

if "CONNECTID2OPENID" not in globals():
	CONNECTID2OPENID = {}

class CPlayer:
	def __init__(self, sOpenID, iConnectID):
		self.m_OpenID = sOpenID
		self.m_ConnectID = iConnectID

		self.m_SendedNum = 0
		self.m_SendedList = []

	def GetConnectID(self):
		return self.m_ConnectID

def MakePlayer(sOpenID, iConnectID):
	return CPlayer(sOpenID, iConnectID)

def AddPlayer(sOpenID, iConnectID, oPlayer):
	global PLAYER_LIST, CONNECTID2OPENID
	if sOpenID in PLAYER_LIST and iConnectID not in CONNECTID2OPENID:
		PrintError("player data is in reset danger!!")
		return
	PLAYER_LIST[sOpenID] = oPlayer
	CONNECTID2OPENID[iConnectID] = sOpenID

def RemovePlayer(sOpenID, iConnectID):
	global PLAYER_LIST, CONNECTID2OPENID
	del PLAYER_LIST[sOpenID]
	del CONNECTID2OPENID[iConnectID]

def GetOnlinePlayer(sOpenID):
	global PLAYER_LIST
	return PLAYER_LIST.get(sOpenID, None)

def GetOnlinePlayerNum():
	global PLAYER_LIST
	return len(PLAYER_LIST)

def GetConnectIDByOpenID(sOpenID):
	global PLAYER_LIST
	oPlayer = PLAYER_LIST.get(sOpenID, None)
	if not oPlayer or (hasattr(oPlayer, "m_OffLine")):
		PrintError("%s has no player object"%sOpenID)
		return -1
	return oPlayer.GetConnectID()

def GetOpenIDByConnectID(iConnectID):
	global CONNECTID2OPENID
	return CONNECTID2OPENID.get(iConnectID, "")

def PlayerOffLine(response, iConnectID):
	sOpenID = GetOpenIDByConnectID(iConnectID)
	who = GetOnlinePlayer(sOpenID)
	RemovePlayer(sOpenID, iConnectID)
	who.m_OffLine = 1
	if SavePlayer():
		del who

def SavePlayer():
	#异步
	return 1