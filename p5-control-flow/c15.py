#
# try...except...else...finally control flow
#

try:
	x = 3
except:
	x = 4
else:
	x += 1
finally:
	print(x)

#
# Context manager
#

# Take#1: Design a class that implements context manager protocol

from sqlite import connect

class Temptable:
	"""A context manager that create and destroy a table named 'points'
	each time it is called."""
	
	def __init__(self, cur):
		self.cur = cur

	def __enter__(self):
		print('__enter__')
		self.cur.execute('create table points(x int, y int)')

	def __exit__(self, exc_type, exc_value, traceback):
		print('__exit__')
		self.cur.execute('drop table points')

# 'connect' is the built-in database context manager
with connect('test.db') as conn: 	
	cur = conn.cursor()
	# 'Temptable' is the previously define context manager
	with Temptable(cur):
		cur.execute('insert into points (x, y) values (1, 2)')
		cur.execute('insert into points (x, y) values (3, 4)')
		for row in cur.execute('select x, y from points')
			print(row)

# Take #2: Using generator function


def temptable(cur):
	cur.execute('create table points(x int, y int)')
	print('created table')
	yield
	cur.execute('drop table points')
	print('dropped table')


class ContextManager:

	def __init__(self, cur):
		self.cur = cur

	def __enter__(self):
		self.gen = temptable(self.cur)
		next(self.gen)
	
	def __exit__(self):
		next(self.gen, None)

with connect('test.db') as conn:
	cur = conn.cursor()
	with ContextManager(cur):
		cur.execute('insert into points (x, y) values (1, 2)')
		cur.execute('insert into points (x, y) values (3, 4)')
		for row in cur.execute('select x, y from points')
			print(row)

# Take #3: Generalize the ContextManager class

class ContextManager:

	def __init__(self, gen):
		# accept any generator function
		self.gen = gen

	def __call__(*args, **kwargs):
		self.args, self.kwargs = args, kwargs
		return self

	def __enter__(self):
		# create a generator instance from abitrary arguments
		self.gen_inst = self.gen(*self.args, **self.kwargs)
		next(self.gen_inst)

	def __exit__(self):
		next(self, gen_inst, None)


ContextManager(temptable)
def temptable(cur):
	# ...

# ...

# Take #4: Using the standard contextmanager decorator

from contextlib import contextmanager

@contextmanager
def temptable(cur):
	cur.execute('create table points(x int, y int)')
	print('created table')
	try:
		yield
	finally:
		cur.execute('drop table points')
		print('dropped table')
