# ping pong
class A:
	def ping(self):
		print('ping:', self)


class B(A):
	def pong(self):
		print('pong:', self)
		# super().ping()

class C(A):
	def pong(self):
		print('PONG:', self)


class D(B, C):
	def ping(self):
		super().ping()
		print('post-ping:', self)

	def pingpong(self):
		self.ping()
		super().ping()
		self.pong()
		super().pong()
		C.pong(self)

# print out method resolution order of a class
def mro(cls):
	print(', '.join(c.__name__ for c in cls.__mro__))

# Inheritance graph example

class A1(object): pass

class A2(object): pass

class A3(A2): pass

class B1(A1, A3): pass
