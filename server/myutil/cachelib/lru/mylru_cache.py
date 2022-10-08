# -*- coding: utf-8 -*-

'''
lru: 缓存策略
'''
from typing import Any, Iterable, Optional, Tuple, Type, Union
from collections import namedtuple
import sys
import time

WRAPPER_ASSIGNMENTS = ('__module__', '__name__', '__qualname__', '__doc__', '__annotations__')
WRAPPER_UPDATES = ('__dict__',)

def update_wrapper(wrapper,
									wrapped,
									assigned = WRAPPER_ASSIGNMENTS,
									updated = WRAPPER_UPDATES):
	for attr in assigned:
		try:
			value = getattr(wrapped, attr)
		except AttributeError:
			pass
		else:
			setattr(wrapper, attr, value)

	for attr in updated:
		getattr(wrapper, attr).update(getattr(wrapped, attr, {}))

	wrapper.__wrapped__ = wrapped
	return wrapper


_CacheInfo = namedtuple("CacheInfo", ["hits", "misses", "maxsize", "currsize"])

class _HashSeq(list):
	__slots__ = 'hashvalue'

	def __init__(self, tup, hash = hash):
		self[:] = tup
		self.hashvalue = hash(tup)

	def __hash__(self):
		return self.hashvalue

def _make_key(args, kwds, typed,
							kwd_mark = (object(),),
							fasttypes = {int, str},
							tuple = tuple, type = type, len = len):
	key = args
	if kwds:
		key += kwd_mark
		for item in kwds.items():
			key += item

	if typed:
		key += tuple(type(v) for v in args)
		if kwds:
			key += tuple(type(v) for v in kwds.values())

	elif len(key) == 1 and type(key[0]) in fasttypes:
		return key[0]

	return _HashSeq(key)

def lru_cache(maxsize = 128, typed = False):
	if isinstance(maxsize, int):
		if maxsize < 0:
			maxsize = 0

	elif callable(maxsize) and isinstance(typed, bool):
		user_function, maxsize = maxsize, 128
		wrapper = _lru_cache_warrper(user_function, maxsize, typed, _CacheInfo)
		return update_wrapper(wrapper, user_function)

	elif maxsize is not None:
		raise TypeError('Expected first argument to be an integer, a callable, or None')

	def decorating_function(user_function):
		wrapper = _lru_cache_warrper(user_function, maxsize, typed, _CacheInfo)
		return update_wrapper(wrapper, user_function)

	return decorating_function

def _lru_cache_warrper(user_function, maxsize, typed, _CacheInfo):
	sentinel = object()
	make_key = _make_key
	PREV, NEXT, KEY, RESULT = 0, 1, 2, 3

	cache = {}
	cache_get = cache.get
	cache_len = cache.__len__

	global root
	root = []
	root[:] = [root, root, None, None]

	localargs = {
		"hits":0,
		"misses":0,
		"full":False,
	}

	if maxsize == 0:
		def wrapper(*args, **kwds):
			localargs["misses"] += 1
			result =  user_function(*args, **kwds)
			return result

	elif maxsize is None:
		def Wrapper(*args, **kwds):
			key = make_key(args, kwds, typed)
			result = cache_get(key, sentinel)
			if result is not sentinel:
				localargs["hits"] += 1
				return result

			localargs["misses"] += 1
			result = user_function(*args, **kwds)
			cache[key] = result
			return result

	else:
		def wrapper(*args, **kwds):
			global root
			key = make_key(args, kwds, typed)
			link = cache_get(key)
			if link is not None:
				link_prev, link_next, key, result = link
				link_prev[NEXT] = link_next
				link_next[PREV] = link_prev
				last = root[PREV]
				last[NEXT] = root[PREV] = link
				link[PREV] = last
				link[NEXT] = root
				localargs["hits"] += 1
				return result

			localargs["misses"] += 1
			result = user_function(*args, **kwds)

			if key in cache:
				pass

			elif localargs["full"]:
				oldroot = root
				oldroot[KEY] = key
				oldroot[RESULT] = result
				root = oldroot[NEXT]
				oldkey = root[KEY]
				oldresult = root[RESULT]
				root[KEY] = root[RESULT] = None
				del cache[oldkey]
				cache[key] = oldroot

			else:
				last = root[PREV]
				link = [last, root, key, result]
				last[NEXT] = root[PREV] = cache[key] = link
				localargs["full"] = (cache_len() >= maxsize)

			localargs["root"] = root
			return result

	def cache_info():
		return _CacheInfo(localargs["hits"], localargs["misses"], maxsize, cache_len())

	def cache_clear():
		cache.clear()
		root[:] = [root, root, None, None]
		localargs["hits"] = 0
		localargs["misses"] = 0
		localargs["full"] = False

	wrapper.cache_info = cache_info
	wrapper.cache_clear = cache_clear

	return wrapper



# @lru_cache()
# def fib_cache(x):
# 	if x == 0 or x == 1:
# 		return x
# 	else:
# 		return fib_cache(x - 1) + fib_cache(x - 2)

# def test():
# 	start = time.time()
# 	result = fib_cache(35)
# 	end = time.time()
# 	PrintDebug("result: %s, use time: %.6f" % (result, end - start))
# 	PrintDebug("cache:", fib_cache.cache_info)

# test()