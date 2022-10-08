# coding=utf-8
"""
tornado协程简化版
"""

from asyncio import CancelledError
from types import GeneratorType
from timer import Call_out

import functools
import sys
from unittest import result
import weakref

__all__ = [
	"coroutine",
	"Return",
	"Future",
	"FutureWrapper",
	"WaitMultifuture",
]

_MY_DEBUG = True

class Return(Exception):
	def __init__(self, value = None):
		super(Return, self).__init__()
		self.value = value

class BadYieldError(Exception):
	pass

class Cancelled(Exception):
	pass

class Future(object):
	def __init__(self):
		super(Future, self).__init__()
		self._done = False
		self._result = None
		self._exc_info = None
		self._callbacks = []
  
	def done(self):
		return self._done

	def result(self):
		#pylint:disable=raising-bad-type
		if self._result is not None:
			return self._result
		if self._exc_info is not None:
			raise self._exc_info
		#assert self.done()
		return self._result

	def add_done_callback(self, fn):
		if self._done:
			fn(self)
		else:
			self._callbacks.append(fn)
   
	def set_result(self, result):
		self._result = result
		self._set_done()
  
	def _set_done(self):
		self._done = True
		for cb in self._callbacks:
			try:
				cb(self)
			except Exception as e:
				PrintError(e)
		self._callbacks = None
  
	def set_exc_info(self, exc_info):
		#简化为Exception，避免栈信息产生内存泄漏
		self._exc_info = exc_info
		self._set_done()
  
	def cancel(self):
		# 取消协程（不执行后续逻辑）
		# 暂时通过抛异常，但不打印的方式，避免内存泄漏
		self._exc_info = Cancelled("user_cancel")
		self._set_done()
  
class FutureWrapper():
	"""回调被卸载时自动取消协程

	NOTE: future内部有循环引用, 外部直接删除回调无法被future感知到。
		之前尝试过用弱引用优化future, 但是有些情况漏考虑导致泄漏	
		所以暂时还是用exception的方式处理cancel操作, 同时封装一层用来兼容外部直接删除回调的写法
	"""
	def __init__(self, oFuture):
		self.m_Future = oFuture
  
	def __call__(self, result):
		try:
			self.m_Future.set_result(result)
		finally:
			self.m_Future = None
   
	def __del__(self):
		try:
			if self.m_Future:
				self.m_Future.cancel()
		finally:
			self.m_Future = None
   
def is_future(future):
	return isinstance(future, Future)

class IOLoop(object):
	def __init__(self, *args, **kwargs):
		self._callbacks = []
		self._running = False
  
	@classmethod
	def current(cls):
		return g_IOLoop

	def add_future(self, future, callback):
		assert isinstance(future, Future)
		future.add_done_callback(
			lambda future: self.add_callback(callback, future))

	def add_callback(self, callback, *args, **kwargs):
		ret = callback(*args, **kwargs)
		if ret is not None:
			try:
				ret = convert_yielded(ret)
			except BadYieldError:
				pass
			else:
				self.add_future(ret, lambda f: f.result())
	
def coroutine(func):
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		future = Future()
		try:
			result = func(*args, **kwargs)
		except (Return, StopIteration) as e:
			result = getattr(e, "value", None)
		except Exception as e:
			PrintError(e)
			future.set_exc_info(e)
			return future
		else:
			if isinstance(result, GeneratorType):
				try:
					yielded = next(result)
				except (Return, StopIteration) as e:
					future.set_result(getattr(e, "value", None))
				except Exception as e:
					PrintError(e)
					future.set_exc_info(e)
				else:
					Runner(result, future, yielded)
				try:
					return future
				finally:
					future = None
		future.set_result(result)
		return future
	return wrapper

def _checklocals(gen):
	# import weakref
	# proxy = weakref.ProxyType
	# o=object
	# o = weakref.proxy(o)
	dLocals = gen.gi_frame.f_locals
	for k, v in dLocals.items():
		if valid(v):
			continue
		raise Exception("参数检查有误")

def valid(v):
	return True

def convert_yielded(yielded):
	if isinstance(yielded, Future):
		return yielded
	raise BadYieldError("yielded unknown object %r"%(yielded, ))

_null_future = Future()
_null_future.set_result(None)

class Runner(object):
	def __init__(self, gen, result_future, first_yielded):
		if _MY_DEBUG:
			_checklocals(gen)
		self.gen = gen
		self.result_future = result_future
		self.future = _null_future
		self.running = False
		self.finished = False
		self.io_loop = IOLoop.current()
		if self.handle_yield(first_yielded):
			self.run()
   
	def run(self):
		if self.running or self.finished:
			return
		try:
			self.running = True
			while True:
				future = self.future
				if not future.done():
					return
				self.future = None
				try:
					try:
						value = future.result()
					except Exception:
						yielded = self.gen.throw(*sys.exc_info())
					else:
						yielded = self.gen.send(value)
				except (Return, StopIteration) as e:
					self.finished = True
					self.future = _null_future
					self.result_future.set_result(getattr(e, "value", None))
					self.result_future = None
					return
				except (Cancelled, ) as e:
					self.finished = True
					self.future = _null_future
					self.result_future.set_exc_info(e)
					self.result_future = None
					return
				except Exception as e:
					self.finished = True
					self.future = _null_future
					self.result_future.set_exc_info(e)
					self.result_future = None
					return
				if _MY_DEBUG:
					_checklocals(self.gen)
				if not self.handle_yield(yielded):
					return
		finally:
			self.running = False
   
	def handle_yield(self, yielded):
		try:
			if _MY_DEBUG:
				self.future = weakref.proxy(convert_yielded(yielded))
			else:
				self.future = convert_yielded(yielded)
		except BadYieldError as e:
			self.future = Future()
			self.future.set_exc_info(e)

		if not self.future.done():
			self.io_loop.add_future(
				self.future, lambda f: self.run())
			return False
		return True

def WaitMultiFuture(lstFuture):
	"""并行协程"""
	#暂不支持dict和set
	if _MY_DEBUG:
		assert all(isinstance(i, Future) for i in lstFuture)
	stUnfinished = set(lstFuture)
	assert len(lstFuture) == len(stUnfinished)
	oFuture = Future()

	if not lstFuture:
		oFuture.set_result([])
		return oFuture

	def _Callback(f):
		stUnfinished.remove(f)
		if stUnfinished:
			return
		lstResult = []
		for f in lstFuture:
			try:
				lstResult.append(f.result())
			except Exception as e:
				oFuture.set_exc_info(e)
				return
		oFuture.set_result(lstResult)
  
	for f in lstFuture:
		f.add_done_callback(_Callback)
	return oFuture
					

if not "g_IOLoop" in globals():
	g_IOLoop = IOLoop()
 
def Sleep(iSec, sFlag):
	def result():
		oFuture.set_result(None)
	oFuture = Future()
	Call_out(iSec, sFlag, result)
	return oFuture