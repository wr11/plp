# -*- coding: utf-8 -*-

from pubdefines import CallManagerFunc

import struct
import pubdefines
import mq

def NetPackagePrepare(byteContent = b""):
	return CNetPackage(byteContent)

class CNetPackage:
	def __init__(self, byteContent):
		self.m_BytesBuffer = byteContent
		self.m_Offset = 0

	def PackInto(self, byteContent):
		self.m_BytesBuffer += byteContent

	def Unpack(self, sType):
		iAddOffset = struct.calcsize(sType)
		byteContent = self.m_BytesBuffer[self.m_Offset:self.m_Offset+iAddOffset]
		self.m_Offset += iAddOffset
		return struct.unpack(sType, byteContent)[0]

	def UnpackEnd(self):
		return self.m_BytesBuffer[self.m_Offset:]

def PacketPrepare(header):
	oNetPack = NetPackagePrepare()
	byteHeader = struct.pack("i", header)
	oNetPack.PackInto(byteHeader)
	return oNetPack

def PacketAddI(iVal, oNetPack):
	if not isinstance(iVal, int):
		iVal = int(iVal)
	byteData = struct.pack("i", iVal)
	if byteData:
		oNetPack.PackInto(byteData)

def PacketAddB(bytes, oNetPack):
	oNetPack.PackInto(bytes)

def PacketAddC(char, oNetPack):
	byteData = struct.pack('c', bytes(char.encode("utf-8")))
	if byteData:
		oNetPack.PackInto(byteData)

def PacketAddS(sVal, oNetPack):
	iLen = len(sVal)
	PacketAddI(iLen, oNetPack)
	if iLen == 1:
		PacketAddC(sVal, oNetPack)
	else:
		byteData = struct.pack('%ss' % len(sVal), sVal.encode("utf-8"))
		if byteData:
			oNetPack.PackInto(byteData)

def PacketSend(iLink, oNetPack):
	oMq = mq.GetMq(pubdefines.MSGQUEUE_SEND)
	bData = oNetPack.m_BytesBuffer
	if oMq:
		if oMq.full():
			PrintWarning("net work delay")
			return
		tFlag = CallManagerFunc("link", "GetClientLink", iLink)
		oMq.put((pubdefines.CLIENT, tFlag, bData))
	del oNetPack
 
def S2SPacketSend(iServer, iIndex, oNetPack):
	oMq = mq.GetMq(pubdefines.MSGQUEUE_SEND)
	bData = oNetPack.m_BytesBuffer
	if oMq:
		if oMq.full():
			PrintWarning("net work delay")
			return
		tFlag = CallManagerFunc("link", "GetLink", iServer, iIndex)
		oMq.put((pubdefines.SERVER, tFlag, bData))
	del oNetPack

'''def PacketSend(iLink, oNetPack):
	oLink = pubdefines.CallManagerFunc("link", "GetLink", iLink)
	if oLink:
		#oLink.m_Socket.transport.write(oNetPack.m_BytesBuffer)
		#oLink.m_Socket.transport.getHandle().sendall(oNetPack.m_BytesBuffer)
	del oNetPack'''

def UnpackPrepare(byteData):
	oNetPackage = NetPackagePrepare(byteData)
	return oNetPackage

def UnpackI(oNetPackage):
	return int(oNetPackage.Unpack("i"))

def UnpackC(oNetPackage):
	return oNetPackage.Unpack("c").decode("utf-8")

def UnpackEnd(oNetPackage):
	return oNetPackage.UnpackEnd()

def UnpackS(oNetPackage):
	iLen = UnpackI(oNetPackage)
	if iLen == 1:
		return UnpackC(oNetPackage)
	else:
		return oNetPackage.Unpack("%ss" % iLen).decode("utf-8")


"""
Format	C Type				Python type			Standard size	Notes
x		pad byte			no value	 	 
c		char				string of length 1	1	 
b		signed char			integer				1				(3)
B		unsigned char		integer				1				(3)
?		_Bool				bool				1				(1)
h		short				integer				2				(3)
H		unsigned short		integer				2				(3)
i		int					integer				4				(3)
I		unsigned int		integer				4				(3)
l		long				integer				4				(3)
L		unsigned long		integer				4				(3)
q		long long			integer				8				(2), (3)
Q		unsigned long long	integer				8				(2), (3)
f		float				float				4				(4)
d		double				float				8				(4)
s		char[]				string				1	 
p		char[]				string	 	 
P		void *				integer	 							(5), (3)

str.encode(‘utf-8')
bytes.decode(‘utf-8')
"""