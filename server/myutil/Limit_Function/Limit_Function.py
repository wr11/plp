# -*- coding: utf-8 -*-
from typing import Any

LIMIT_REGION = ["Limit_Function",]

class LimitFuncError(TypeError):pass

class _LimitFunction(object):

	def __setattr__(self, name: str, value: Any) -> None:
		if name in self.__dict__.keys():
			raise LimitFuncError("LimitFunction illegal use: cannot be reassigned!")
		else:
			self.__dict__[name]=value

	@staticmethod
	def Limit():
		modulename = __name__
		PrintDebug("modluname")
		PrintDebug(modulename)
		def func1(func):
			if modulename not in LIMIT_REGION:
				raise LimitFuncError("LimitFunction illegal use: wrong modulename!")
			return func
		return func1

# import sys
# sys.modules[__name__] = _LimitFunction()

'''
#test:
@_LimitFunction.Limit()
def A():
	PrintDebug("A is called")

limitfunction = _LimitFunction()
limitfunction.a = A
'''