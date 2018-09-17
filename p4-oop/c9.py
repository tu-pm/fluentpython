from array import array
import math

# Pythonic Vector2d implementation

class Vector2d(object):
	typecode = 'd'

	def __init__(self, x, y):
		self.__x = float(x)
		self.__y = float(y)

	@property
	def x(self):
		return self.__x
	
	@property
	def y(self):
		return self.__y
	
	def __iter__(self):
		return (i for i in (self.x, self.y))

	def __repr__(self):
		class_name = type(self).__name__
		return '{}({!r}, {!r})'.format(class_name, *self)

	def __str__(self):
		return str(tuple(self))

	def __eq__(self, other):
		return type(self) == type(other) and tuple(self) == tuple(other)

	def __hash__(self):
		return hash(self.x) ^ hash(self.y)

	def __abs__(self):
		return math.hypot(self.x, self.y)

	def __bool__(self):
		return bool(abs(self))

	def __complex__(self):
		return complex(self.x, self.y)

	def angle(self):
		return math.atan2(self.y, self.x)

	def __format__(self, fmt_spec=''):
		if fmt_spec.endswith('p'):
			fmt_spec = fmt_spec[:-1]
			coords = (abs(self), self.angle())
			outer_fmt = '<{}, {}>'
		else:
			coords = self
			outer_fmt = '({}, {})'
		components = (format(c, fmt_spec) for c in coords)
		return outer_fmt.format(*components)

f = '{:p}'
x = Vector2d(3, 4)

# Multiple constructors

class Foo(object):
	
	def __init__(self, file):
		self.file = file

	@classmethod
	def fromfilename(cls, filename):
		file = open(filename, 'rb')
		return cls(file)
	
