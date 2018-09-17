# FrenchDeck implements MutableSequences

import collections

Card = collections.namedtuple('Card', ['rank', 'suit'])

class FrenchDeck(collections.MutableSequence):
	ranks = tuple(str(i) for i in range(2, 11)) + tuple('JQKA')
	suits = 'spades diamonds clubs hearts'.split()

	def __init__(self):
		self._cards = [Card(rank, suit) for suit in self.suits
										for rank in self.ranks]

	def __len__(self):
		return len(self._cards)

	def __getitem__(self, position):
		return self._cards[position]

	def __setitem__(self, position, value):
		self._cards[position] = value

	def __delitem__(self, position):
		del(self._cards[position])

	def insert(self, position, value):
		self._cards.insert(position, value)

x = FrenchDeck()

# Tombola ABC

import abc

class Tombola(abc.ABC):

	@abc.abstractmethod
	def load(self, iterable):
		"""Add items from an iterable"""

	@abc.abstractmethod
	def pick(self):
		"""Remove item at random, returning it.

		This method should raise `LookupError` when the instance is empty
		"""

	def loaded(self):
		"""Return `True` if there's at least 1 item, `False` otherwise"""
		return bool(self.inspect())

	def inspect(self):
		"""Return a sorted tuple with the items currently inside."""
		items = []
		while True:
			try:
				items.append(self.pick())
			except LookupError:
				break
		self.load(items)
		return tuple(sorted(items))

# Concrete class BingoCage, subclassing Tombola

import random

class BingoCage(Tombola):

	def __init__(self, items):
		self._randomizer = random.SystemRandom()
		self._items = []
		self.load(items)

	def load(self, items):
		self._items.extend(items)
		self._randomizer.shuffle(self._items)

	def pick(self):
		try:
			return self._items.pop()
		except IndexError:
			raise LookupError('pick from empty BingoCage')

	def __call__(self):
		self.pick()

class LotteryBlower(Tombola):
	
	def __init__(self, iterable):
		self._balls = list(iterable)

	def load(self, iterable):
		self._balls.extend(iterable)

	def pick(self):
		try:
			position = random.randrange(len(self._balls))
		except ValueError:
			raise LookupError('pick from empty LotteryBlower')
		return self._balls.pop(position)

	def loaded(self):
		return bool(self._balls)

	def inspect(self):
		return tuple(sorted(self._balls))

@Tombola.register
class TomboList(list):
	
	load = list.extend

	def pick(self):
		if self:
			position = randrange(len(self))
			return self.pop(position)
		else:
			raise LookupError('pop from empty TomboList')

	def loaded(self):
		return bool(self)


	def inspect(self):
		return tuple(sorted(self))