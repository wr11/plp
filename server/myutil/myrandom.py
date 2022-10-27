# -*- coding: utf-8 -*-
import random

def GetUniqueRandomIDList(lstID, iCount):
	if len(lstID) < iCount:
		return list(lstID)
	return random.sample(lstID, iCount)