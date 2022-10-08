# -*- coding: utf-8 -*-

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
'''以上的代码是怎样的工作的呢？

理解它需要对Python虚拟机的函数调用有一定的理解。其实以上代码和其他语言对尾递归的调用的优化原理都是相似的,那就是在尾递归调用的时候重复使用旧的栈帧, 因为之前说过, 尾递归本身在调用过程中, 旧的栈帧里面那些内容已经没有用了, 所以可以被复用。

Python的函数调用首先要了解code object, function object, frame object这三个object(对象), code object是静态的概念, 是对一个可执行的代码块的抽象, module, function, class等等都会被生成code object, 这个对象的属性包含了”编译器”(Python是解释型的，此处的编译器准确来说只是编译生成字节码的)对代码的静态分析的结果, 包含字节码指令, 常量表, 符号表等等。function object是函数对象, 函数是第一类对象, 说的就是这个对象。当解释器执行到def fib(...)语句的时候(MAKE_FUNCTION), 就会基于code object生成对应的function object。

但是生成function object并没有执行它, 当真正执行函数调用的时候, fib(...)这时候对应的字节码指令(CALL_FUNCITON), 可以看一下, CPython的源码, 真正执行的时候Python虚拟机会模拟x86CPU执行指令的大致结构, 而运行时栈帧的抽象就是frame obejct, 这玩意儿就模拟了类似C里面运行时栈, 寄存器等等运行时状态, 当函数内部又有函数调用的时候, 则又会针对内部的嵌套的函数调用生成对应的frame object, 这样看上去整个虚拟机就是一个栈帧连着又一个栈帧, 类似一个链表, 当前栈帧通过f_back这个指针指向上一栈帧, 这样你才能在执行完毕, 退出当前帧的时候回退到上一帧。和C里执行栈的增长退出模式很像。

frame object栈帧对象只有在当前函数执行的时候才会产生, 所以你只能在函数内通过sys._getframe()调用来获取当前执行帧对象。通过f.f_back获取上一帧, f.f_back.f_back来获取当前帧的上一帧的上一帧(当前帧的“爷爷”)。

另外一个需要注意到的是, 对于任何对尾递归而言, 其执行过程可以线性展开, 此时你会发现, 最终结果的产生完全可以从任意中间状态开始计算, 最终都能得到同样的执行结果。如果把函数参数看作状态(state_N)的话, 也就是tail_call(state_N)->tail_call(state_N-1)->tail_call(state_N-2)->...->tail_call(state_0), state_0是递归临界条件, 也就是递归收敛的最终状态, 而你在执行过程中, 从任一起始状态(state_N)到收敛状态(state_0)的中间状态state_x开始递归, 都可以得到同样的结果。

当Python执行过程中发生异常(错误)时(或者也可以直接手动抛出raise ...), 该异常会从当前栈帧开始向旧的执行栈帧传递, 直到有一个旧的栈帧捕获这个异常, 而该栈帧之后(比它更新的栈帧)的栈帧就被回收了。

有了以上的理论基础, 就能理解之前代码的逻辑了:

尾递归函数fib被tail_call_optimized装饰, 则fib这个名字实际所指的function object变成了tail_call_optimized里return的_wrapper, fib 指向_wrapper。

注意_wrapper里return func(*args, **kwargs)这句, 这个func还是未被tail_call_optimized装饰的fib（装饰器的基本原理）, func是实际的fib, 我们称之为real_fib。

当执行fib(1200, 0, 1)时, 实际是执行_wrapper的逻辑, 获取帧对象也是_wrapper对应的, 我们称之为frame_wapper。

由于我们是第一次调用, 所以”if f.f_back and f.f_back.f_back and f.f_code == f.f_back.f_back.f_code”这句里f.f_code==f.f_back.f_back.f_code显然不满足。

继续走循环, 内部调用func(*args, **kwargs), 之前说过这个func是没被装饰器装饰的fib, 也就是real_fib。

由于是函数调用, 所以虚拟机会创建real_fib的栈帧, 我们称之为frame_real_fib, 然后执行real_fib里的代码, 此时当前线程内的栈帧链表按从旧到新依次为:

旧的虚拟机栈帧，frame_wrapper，frame_real_fib(当前执行帧)
real_fib里的逻辑会走return fib(n-1, b, a+b), 有一个嵌套调用, 此时的fib是谁呢？此时的fib就是我们的_wrapper, 因为我们第一步说过, fib这个名字已经指向了_wrapper这个函数对象。

依然是函数调用的一套, 创建执行栈帧, 我们称之为frame_wrapper2, 注意： 执行栈帧是动态生成的, 虽然对应的是同样函数对象(_wrapper), 但依然是不同的栈帧对象, 所以称之为frame_wrapper2。 今后进入frame_wrapper2执行, 注意此时的虚拟机的运行时栈帧的结构按从旧到新为:

旧的虚拟机栈帧、frame_wrapper、frame_real_fib、frame_wrapper2(当前执行栈帧)
进入frame_wrapper2执行后, 首先获取当前执行帧, 即frame_wrapper2, 紧接着, 执行判断, 此时:

if f.f_back and f.f_back.f_back and f.f_code == f.f_back.f_back.f_code
以上这句就满足了, f.f_code是当前帧frame_wrapper2的执行帧的code对象, f.f_back.f_back.f_code从当前的执行帧链表来看是frame_wrapper的执行帧的code对象, 很显然他们都是同一个code块的code object(def _wrapper…..)。于是抛出异常, 通过异常的方式, 把传过来的参数保留, 然后, 异常向旧的栈帧传递, 直到被捕获, 而之后的栈帧被回收, 即抛出异常后, 直到被捕获时, 虚拟机内的执行帧是:

旧的虚拟机栈帧、frame_wrapper(当前执行帧)
于是现在恢复执行frame_wrapper这个帧, 直接顺序执行了, 由于是个循环, 同时参数通过异常的方式被捕获, 所以又进入了return func(*args, **kwargs)这句, 根据我们之前说的, 尾递归从递归过程中任意中间状态都可以收敛到最终状态, 所以就这样, 执行两个帧, 搞出中间状态, 然后抛异常, 回收两个帧, 这样一直循环直到求出最终结果。

在整个递归过程中, 没有频繁的递归一次, 生成一个帧, 如果你不用这个优化, 可能你递归1000次, 就要生成1000个栈帧, 一旦达到递归栈的深度限制, 就挂了。

使用了这个装饰器之后, 最多生成3个帧, 随后就被回收了, 所以是不可能达到递归栈的深度的限制的。

注意： 这个装饰器只能针对尾递归使用。'''