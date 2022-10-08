import sys

class TailCallException(BaseException):
	def __init__(self, args, kwargs):
		self.args = args
		self.kwargs = kwargs

def tail_call_optimized(func):
	def _wrapper(*args, **kwargs):
		f = sys._getframe()
		if f.f_back and f.f_back.f_back and f.f_code == f.f_back.f_back.f_code:
			raise TailCallException(args, kwargs)

		else:
			while True:
				try:
					return func(*args, **kwargs)
				except TailCallException as e:
					args = e.args
					kwargs = e.kwargs
	return _wrapper

@tail_call_optimized
def fib(n, a, b):
	if n == 1:
		return a
	else:
		return fib(n-1, b, a+b)

# r = fib(1200, 0, 1) #突破了调用栈的深度限制