# -*- coding: utf-8 -*-
import functools
from sys import maxsize
import types

__all__ = ["CacheResult", ]

#_VALID_ARGTYPE = {types.NoneType, int, long, str}
_VALID_ARGTYPE = {int, str}

if not "g_CacheList" in globals():
	g_CacheList = {}
	
def CacheResult(max_size = 1000):
	def decoration_function(user_function):
		global g_CacheList
		cache = {}
		cache_get = cache.get
		
		sentinel = object()
		func_name = "%s.%s" % (user_function.__module__, user_function.__name__)
		g_CacheList[func_name] = cache
		
		@functools.wraps(user_function)
		def wrapper(*args, **kwds):
			key = _MakeKey(args, kwds)
			result = cache_get(key, sentinel)
			if result is not sentinel:
				return result
			result = user_function(*args, **kwds)
			cur_size = len(cache)
			if cur_size <= maxsize:
				cache[key] = result
			else:
				PrintWarning("cache overflow")
			return result
		
		return wrapper
	
	return decoration_function

def ClearCache(user_function):
	global g_CacheList
	func_name = "%s.%s" % (user_function.__module__, user_function.__name__)
	cache = g_CacheList.get(func_name, None)
	if cache:
		cache.clear()
		
def _AssertArgType(args, kwds):
	for v in args:
		assert type(v) in _VALID_ARGTYPE
	for v in kwds.itervalues():
		assert type(v) in _VALID_ARGTYPE
		
def _MakeKey(args, kwds):
	_AssertArgType(args, kwds)
	if not kwds:
		return args
	return args, sum(kwds.iteritems(), ())