from functools import wraps

#
# Simple coroutine example
#
def count2inf():
	i = 0
	while True:
		x = yield i
		i += 1
		print(x)

#
# automatically priming with decorator
#
def coroutine(func):
	"""Decorator: primes `func` by advancing to first `yield`"""
	@wraps(func)
	def primer(*args, **kwargs):
		gen = func(*args, **kwargs)
		next(gen)
		return gen
	return primer

#
# Interactive coroutine averager
#

@coroutine
def averager():
	total = 0.0
	count = 0
	average = None

	while True:
		term = yield average
		total += term
		count += 1
		average = total / count

#
# Averager with return statement
#

from collections import namedtuple

Result = namedtuple('Result', ['count', 'average'])


def averager()
	total = 0.0
	count = 0
	average = None
	while True:
		if term is None:
			break
		term = yield
		total += term
		count += 1
		average = total / count

	return Result(count, average)