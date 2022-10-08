class CMap(object):
	def __init__(self):
		self.m_iWidth = 0
		self.m_iHeight = 0
		self.m_MapData = []
		self.m_TestPoint = []

	def SetData(self, mapData):
		'''
		m_MapData[x][y]为坐标(x,y)的阻挡信息
		:param ampData:
		:return:
		'''
		self.m_MapData = mapData
		self.m_iWidth = len(mapData)
		self.m_iHeight = len(mapData[0])

	def IsBlock(self, x, y):
		'''
		采用笛卡尔坐标系
		:param x: 横坐标
		:param y: 纵坐标
		:return:0:表示非阻挡，1表示阻挡
		'''
		return self.m_MapData[x][y]

	def SetTestPoint(self, testPoint):
		'''
		用于测试是否在最大闭合区域的点
		:param testPoint:
		:return:
		'''
		self.m_TestPoint = map(tuple, testPoint)

	@classmethod
	def CreateMap(cls, dInfo):
		'''
		地图数据的加载
		:param fpath:
		'''
		mapData = dInfo.get("MapData", [])
		testPoint = dInfo.get("TestPoint", [])
		oMap = CMap()
		oMap.SetData(mapData)
		oMap.SetTestPoint(testPoint)
		return oMap

def main(argv):
	oMap = CreateMap(argv)

	lstMapdata = oMap.m_MapData
	iValidWidth = oMap.m_iWidth - 1
	iValidHeight = oMap.m_iHeight - 1
	lstLine = [[]]
	lstRangeW = range(1, iValidWidth)
	lstRangeH = range(1, iValidHeight)
	for x in lstRangeW:
		lstVal = []
		iVal = 0
		iNum = 0
		lstTemp = lstMapdata[x]
		for y in lstRangeH:
			if lstTemp[y] == 0:
				iVal |= (1 << y)
				iNum += 1
			elif iVal:
				lstVal.append((iVal, iNum))
				iVal = 0
				iNum = 0
		if iVal:
			lstVal.append((iVal, iNum))
		lstLine.append(lstVal)
	lstLine.append([])

	iAreaIdx = 0
	dArea = {}
	dVal2Area = {}
	dRef = {}
	for iVal, iNum in lstLine[1]:
		tVal = (1, iVal)
		dArea[iAreaIdx] = [{1:iVal}, iNum]
		dVal2Area[tVal] = iAreaIdx
		iAreaIdx += 1
	for x in range(2, iValidWidth):
		iLastX = x - 1
		lstVal1 = lstLine[iLastX]
		lstVal2 = lstLine[x]
		iStart = 0
		iCnt =1
		for iVal2, iNum2 in lstVal2:
			tVal2 = (x, iVal2)
			bConnect = False
			iStart = iStart + iCnt - 1
			iCnt = 0
			for iVal1, _ in lstVal1[iStart:]:
				if iVal1&iVal2:
					iID = dVal2Area[(iLastX, iVal1)]
					while(iID in dRef):
						iID = dRef[iID]
					if not bConnect:
						bConnect = True
						dVal2Area[tVal2] = iID
						dAreaVal = dArea[iID][0]
						if x in dArea:
							dAreaVal[x] |= iVal2
						else:
							dAreaVal[x] = iVal2
						dArea[iID][1] += iNum2
					else:
						iOldID = dVal2Area[tVal2]
						while(iOldID in dRef):
							iOldID = dRef[iOldID]
						if iOldID != iID:
							if len(dArea[iID][0]) > len(dArea[iOldID][0]):
								iSmall = iOldID
								iBig = iID
							else:
								iSmall = iOldID
								iBig = iID
							dAreaVal = dArea[iBig][0]
							for iTempX, iTempVal in dArea[iSmall][0].items():
								if iTempX in dAreaVal:
									dAreaVal[iTempX] |= iTempVal
								else:
									dAreaVal[iTempX] = iTempVal
							dArea[iBig][1] += dArea[iSmall][1]
							dRef[iSmall] = iBig
							del dArea[iSmall]
				elif bConnect:
					break
				iCnt += 1
			if not bConnect:
				iCnt = 1
			if not tVal2 in dVal2Area:
				dArea[iAreaIdx] = [{x:iVal2}, iNum2]
				dVal2Area[tVal2] = iAreaIdx
				iAreaIdx += 1

	iMaxAreaID = 0
	iMaxCnt = 0
	for iAreaID, (_, iNum) in dArea.items():
		if iNum > iMaxCnt:
			iMaxCnt = iNum
			iMaxAreaID = iAreaID

	dMaxArea = dArea[iMaxAreaID][0]
	lstResult = []
	for iTestX, iTestY in oMap.m_TestPoint:
		if iTestX < 1 or iTestX >= iValidWidth or iTestY <1 or iTestY >= iValidHeight:
			continue
		if not iTestX in dMaxArea:
			continue
		if (1 << iTestY) & dMaxArea[iTestX]:
			lstResult.append((iTestX, iTestY))

	return lstResult

def CreateMap(dInfo):
	return CMap.CreateMap(dInfo)