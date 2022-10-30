# coding:utf-8

import datahub.datashadow as shadow

# Player Shadow
def LoadPlayerDataShadow(oResponse, sOpenID, lstAttr):
	oShadow = shadow.CreatePlayerDataShadow(sOpenID, lstAttr)
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
	oResponse(10, data)

def CreateNewPlayer(oShadow):
	oShadow.SaveToDataBase()

def CheckDataValid(oShadow):
	return True

def UpdatePlayerShadowData(oResponse, data):
	iRet = 0
	try:
		for sOpenID, dData in data.items():
			if not dData:
				continue
			oShadow = shadow.GetPlayerShadowByOpenID(sOpenID)
			if not oShadow:
				oShadow = shadow.CreatePlayerDataShadow(sOpenID)
			oShadow.Update(dData)
		iRet = 1
	except Exception as e:
		PrintError(e)
		iRet = 0
	oResponse(iRet)

# Game Shadow
def LoadGameShadow(oResponse, sGameName, lstAttr):
	oShadow = shadow.CreateGameShadow(sGameName, lstAttr)
	data = oShadow.LoadDataFromDataBase()
	if not data:
		data = {}
		CreateNewGameShadow(oShadow)
	oResponse(data)

def CreateNewGameShadow(oShadow):
	oShadow.SaveToDataBase()

def UpdateGameShadowData(oResponse, data):
	for sGameName, dData in data.items():
		if not dData:
			continue
		oShadow = shadow.GetGameShadowByGameName(sGameName)
		if not oShadow:
			oShadow = shadow.CreateGameShadow(sGameName)
		oShadow.Update(dData)

#listcontainer shadow
def ListContainerSaveToDBS(oResponse, data):
	for sType, lstData in data.items():
		oShadow = shadow.GetListContainerShadowByType(sType)
		if not oShadow:
			oShadow = shadow.CreateListContainerShadow(sType)
		oShadow.SetData(lstData)
		oShadow.SaveToDataBase()

def LoadDataFromTableShadow(oResponse, sType, sSelectType):
	oShadow = shadow.GetListContainerShadowByType(sType)
	if not oShadow:
		oShadow = shadow.CreateListContainerShadow(sType)
	data = oShadow.LookUp(sSelectType)
	oResponse(data)

def LoadMultiDataFromTableShadow(oResponse, sType, sSelectType, lstPrimaryData):
	oShadow = shadow.GetListContainerShadowByType(sType)
	if not oShadow:
		oShadow = shadow.CreateListContainerShadow(sType)
	data = oShadow.LookUp(sSelectType, filter = lstPrimaryData)
	oResponse(data)