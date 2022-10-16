# coding:utf-8

import datahub.datashadow as shadow

# Player Shadow
def LoadPlayerDataShadow(oResponse, sOpenID):
	oShadow = shadow.CreatePlayerDataShadow(sOpenID)
	data = oShadow.LoadDataFromDataBase()
	if not data:
		try:
			data = oShadow.Save()
			CreateNewPlayer(oShadow)
		except Exception as e:
			oResponse(11, {})
			PrintError(e)
			return
	else:
		if not CheckDataValid(oShadow):
			oResponse(12, {})
			return
	oResponse(1, data)

def CreateNewPlayer(oShadow):
	oShadow.SaveToDataBase()

def CheckDataValid(oShadow):
	return True

def UpdatePlayerShadowData(oResponse, data):
	PrintDebug("update player shadow",data)
	for sOpenID, dData in data.items():
		if not dData:
			continue
		oShadow = shadow.GetPlayerShadowByOpenID(sOpenID)
		if not oShadow:
			oShadow = shadow.CreatePlayerDataShadow(sOpenID)
		oShadow.Update(dData)

# Game Shadow
def LoadGameShadow(oResponse, sGameName, lstAttr):
	oShadow = shadow.CreateGameShadow(sGameName)
	oShadow.Setattr(lstAttr)
	data = oShadow.LoadDataFromDataBase()
	if not data:
		data = {}
		CreateNewGameShadow(oShadow)
	oResponse(data)

def CreateNewGameShadow(oShadow):
	oShadow.SaveToDataBase()

def UpdateGameShadowData(oResponse, data):
	PrintDebug("update game shadow",data)
	for sGameName, dData in data.items():
		if not dData:
			continue
		oShadow = shadow.GetGameShadowByGameName(sGameName)
		if not oShadow:
			oShadow = shadow.CreateGameShadow(sGameName)
		oShadow.Update(dData)