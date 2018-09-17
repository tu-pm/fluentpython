class Foo(object):
	x = 'a'

	def __init__(self):
		pass

foo1 = Foo()
foo2 = Foo()

foo1.x = foo2.x