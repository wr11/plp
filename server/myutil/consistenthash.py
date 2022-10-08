import zlib
import bisect
from hashlib import md5
import collections

class NodeCollision(Exception):
	pass

class CConsistentHash():
	def __init__(self, replicas=100):
		"""
		@param replicas: 虚拟节点数量
		"""
		assert replicas > 1
		self.m_Replicas = replicas
		self.m_Ring = []
		self.m_Nodes = {}
		self.m_NodeHash = collections.defaultdict(list)
		self._InitHash = lambda x: int(md5(x).hexdigest(), 16)%0xffffffff - 0x7fffffff
		self._KeyHash = zlib.crc32
		
	def GetAllNodeName(self):
		return self.m_NodeHash.keys()
	
	def AddNode(self, sName, node):
		"""增加节点
		NOTE: 没有处理哈希冲突
		@param sName: 节点名称(str 唯一标识)
		@param node: 节点对象(用于返回节点名称)
		"""
		assert sName not in self.m_NodeHash
		stHash = set()
		for i in range(self.m_Replicas):
			sVName = "%s-%s" % (sName, i)
			h = self._InitHash(sVName)
			if h in self.m_Nodes or h in stHash:
				raise NodeCollision("err vnode: %s" % sVName)
			stHash.add(h)
		for h in stHash:
			self.m_Nodes[h] = node
			self.m_NodeHash[sName].append(h)
			bisect.insort(self.m_Ring, h)
			
	def DelNode(self, sName):
		"""删除节点"""
		lst = self.m_NodeHash.pop(sName)
		for h in lst:
			del self.m_Nodes[h]
			index = bisect.bisect_left(self.m_Ring, h)
			del self.m_Ring[index]
			
	def GetNodeByKey(self, sKey):
		"""根据key获取节点
		@param sKey: str 任意str
		@return: 节点对象
		"""
		start = bisect.bisect(self.m_Ring, self._KeyHash(sKey))
		if start == len(self.m_Ring):
			start = 0
		return self.m_Nodes[self.m_Ring[start]]