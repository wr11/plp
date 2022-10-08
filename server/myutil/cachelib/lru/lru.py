from defines import *

class CLru:
	def __init__(self, size):
		self.m_InitLimit = size
		self.m_CurLimit = size
		self.m_DoubleLink = []
		self.m_HashMap = dict()
		self.InitData()

	def InitData(self):
		self.m_HashMap.clear()
		self.m_DoubleLink[:] = [self.m_DoubleLink, self.m_DoubleLink, None, None]

		self.m_CurLimit = self.m_InitLimit
		self.m_Hits = 0
		self.m_Misses = 0
		self.m_MaxSize = 0
		self.m_ExpandCnt = 0
		self.m_ReduceCnt = 0

	def __len__(self):
		return len(self.m_HashMap)

	def Keys(self):
		return self.m_HashMap.keys()

	def Values(self):
		return [node[VALUE] for key, node in self.m_HashMap.iteritems()]

	def Items(self):
		return [(key, node[VALUE]) for key, node in self.m_HashMap.iteritems()]

	def Clear(self):
		self.InitData()

	def CurrentSize(self):
		return len(self.m_HashMap)

	def AddLimit(self, iLimit):
		'''
		动态更新阀值
		'''
		self.m_CurLimit += iLimit
		self.m_CurLimit = max(1, self.m_CurLimit)

		if iLimit > 0:
			self.m_ExpandCnt += 1
		elif iLimit < 0:
			self.m_ReduceCnt += 1

	def ValidRemove(self, key, obj):
		if self.IsActive(key, obj):
			return 0
		return 1

	def SetValue(self, key, value):
		'''
		更新值，更新k-v在双向链表中的位置
		'''
		if key in self.m_HashMap:
			return

		node_head = self.m_DoubleLink[PREV]
		node = [node_head, self.m_DoubleLink, key, value]
		node_head[NEXT] = self.m_DoubleLink[PREV] = self.m_HashMap[key] = node
		self.m_MaxSize = max(self.m_MaxSize, len(self.m_HashMap))

	def GetValue(self, key):
		'''
		获取对应key的缓存值，并更新数据为热数据，放在双向链表的头部
		'''
		node = self.m_HashMap.get(key, None)
		if not node:
			return

		node_prev, node_next, k, v = node
		node_prev[NEXT] = node_next
		node_next[PREV] = node_prev

		node_head = self.m_DoubleLink[PREV]
		node_head[NEXT] = self.m_DoubleLink[PREV] = node

		node[PREV] = node_head
		node[NEXT] = self.m_DoubleLink

		return v

	def RemoveValue(self, key):
		'''
		删除对应key的缓存值
		'''
		node = self.m_HashMap.pop(key, None)
		if not node:
			return
		
		node_prev, node_next, k, v = node
		node[PREV] = node[NEXT] = None
		node_prev[NEXT] = node_next
		node_next[PREV] = node_prev

	def CacheInfo(self):
		dInfo = {
			"size": len(self.m_HashMap),
			"threshold":self.m_InitLimit,
			"limit":self.m_CurLimit,
			"max":self.m_MaxSize,
			"expand":self.m_ExpandCnt,
			"reduce":self.m_ReduceCnt,
			"hits":self.m_Hits,
			"misses":self.m_Misses,
			"hitrate":self.m_Hits*100.0/max(1, self.m_Misses + self.m_Hits),
		}
		return dInfo

	def GetObject(self, key):
		'''
		查找缓存对象，查找失败创建新对象
		'''
		obj = self.GetValue(key)
		if obj:
			self.m_Hits += 1
			return obj

		self.m_Misses += 1
		obj = self.NewObject(key)

		self.SetValue(key, obj)
		return obj

	def FindObject(self, key):
		'''
		查找缓存对象，查找失败不创建
		'''
		obj = self.GetValue(key)
		if obj:
			self.m_Hits += 1
			return obj

		self.m_Misses += 1
		return None

	def NewObject(self, key):
		'''
		生成缓存对象，子类实现
		'''
		return None

	def Active(self, key, obj):
		'''
		缓存对象命中时由系统触发，子类实现
		'''
		pass

	def UnActive(self, key, obj):
		'''
		缓存对象从内存中淘汰时由系统触发，子类实现
		'''
		pass

	def IsActive(self, key, obj):
		'''
		判断对象是否活跃，是否允许从内存中淘汰，子类实现
		'''
		return 0


# cache = CLru(128)
# cache.SetValue("test", 1)
# cache.SetValue("test", 2)
# PrintDebug(cache.FindObject("test"))
# PrintDebug(cache.CacheInfo())