# coding:utf-8

import datahub.datashadow as shadow

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
	PrintDebug("update shadow",data)
	for sOpenID, dData in data.items():
		if not dData:
			continue
		oShadow = shadow.GetPlayerShadowByOpenID(sOpenID)
		if not oShadow:
			oShadow = shadow.CreatePlayerDataShadow(sOpenID)
		oShadow.Update(dData)