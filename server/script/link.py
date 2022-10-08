# -*- coding: utf-8 -*-

import pubdefines

def Init():
	oLinkManager = CLinkManager()
	if not pubdefines.GetGlobalManager("link"):
		pubdefines.SetGlobalManager("link", oLinkManager)

class CLinkManager:
	def __init__(self):
		self.m_LinkDict = {}
		self.m_ClientLink = {}

	def AddLink(self, sHost, iPort, iServer, iIndex):
		tFlag = (iServer, iIndex)
		if tFlag not in self.m_LinkDict:
			self.m_LinkDict[tFlag] = (sHost, iPort)
		else:
			PrintWarning("link repeated %s %s %s %s"%(sHost, iPort, iServer, iIndex))

	def DelLink(self, iServer, iIndex):
		tFlag = (iServer, iIndex)
		if tFlag in self.m_LinkDict:
			del self.m_LinkDict[tFlag]

	def GetLink(self, iServer, iIndex):
		tFlag = (iServer, iIndex)
		return self.m_LinkDict.get(tFlag, ())

	def AddClientLink(self, sIP, iPort, iConnectID):
		if iConnectID not in self.m_ClientLink:
			self.m_ClientLink[iConnectID] = (sIP, iPort)
		else:
			PrintWarning("clientlink repeated %s %s"%(sIP, iPort))

	def GetClientLink(self, iConnectID):
		return self.m_ClientLink.get(iConnectID, ())

	def DelClientLink(self, iConnectID):
		if iConnectID in self.m_ClientLink:
			del self.m_ClientLink[iConnectID]