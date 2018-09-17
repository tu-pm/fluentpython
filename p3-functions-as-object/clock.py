import time
import functools
import  html

#
# functools.wraps
#

def clock1(func):
    def clocked(*args):
        t0 = time.time()
        result = func(*args)
        elapsed = time.time() - t0
        print('Took %s seconds' % elapsed)
        return result
    return clocked

def clock2(func):
    @functools.wraps(func)
    def clocked(*args, **kwargs):
        t0 = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - t0
        print('Took %s seconds' % elapsed)
        return result
    return clocked

@clock1
def add(x, y):
	return x + y

@clock2
def mul(x, y):
	return x * y

#
# functools.lru_cache
#

def clock(func):
	@functools.wraps(func)
	def clocked(*args, **kwargs):
		t0 = time.time()
		result = func(*args, **kwargs)
		elapsed = time.time() - t0
		name = func.__name__
		arg_lst = []
		if args:
			arg_lst.append(', '.join(repr(arg) for arg in args))
		if kwargs:
			pairs = ['%s=%r' % (k, w) for k, w in sorted(kwargs.items())]
			arg_lst.append(', '.join(pairs))
		arg_str = ', '.join(arg_lst)
		print('[%0.8fs] %s(%s) -> %r ' % (elapsed, name, arg_str, result))
		return result
	return clocked

@clock
def fibonacci(n):
	return n if n < 2 else fibonacci(n-1) + fibonacci(n-2)

@functools.lru_cache()
@clock
def optimized_fibonacci(n):
	return n if n < 2 else optimized_fibonacci(n-1) + optimized_fibonacci(n-2)

#
# functools.singledispatch
#

from functools import singledispatch
from collections import abc
import numbers
import html

@singledispatch
def htmlize(obj):
    content = html.escape(repr(obj))
    return '<pre>{}</pre>'.format(content)

@htmlize.register(str)
def _(text):
    content = html.escape(text).replace('\n', '<br>\n')
    return '<p>{0}</p>'.format(content)

@htmlize.register(numbers.Integral)
def _(n):
    return '<pre>{0} (0x{0:x})</pre>'.format(n)

@htmlize.register(tuple)
@htmlize.register(abc.MutableSequence)
def _(seq):
    inner = '</li>\n<li>'.join(htmlize(item) for item in seq)
    return '<ul>\n<li>' + inner + '</li>\n</ul>'

#
# Parameterized Decorator
#

def outerdeco(*decoargs):
	def innerdeco(func):
		def innerfunc(*args, **kwargs):
			num_args = len(decoargs)
			print('The outer decorator took %s arguments' % num_args)
			return func(*args, **kwargs)
		return innerfunc
	return innerdeco

@outerdeco(1, 2, 3, 4, 5)
def add(x, y):
	return x + y