## Chapter 11: Interfaces - From Protocols to ABCs

Chủ đề của chương này là *interface*: từ những interface không chính thức, hay còn gọi là *protocol*, cho đến abstract base classes (ABCs) định nghĩa interfaces một cách rõ ràng và bắt buộc phải tuân thủ.

Với những bạn đọc có nền tảng về Java, C# hay Golang, protocol hay duck-typing có thể là một ý tưởng mới, thậm chí là đột phá. Nhưng đối với những người lập trình Python hay Ruby lâu năm, protocol là cách sử dụng interface quá đỗi bình thường và quen thuộc. Thậm chí phải mất 15 năm, các nhà phát triển mới quyết định đưa interface "chính thức", hay ABCs, vào Python.

Trong chapter này ta sẽ đi sâu vào tìm hiểu quá trình phát triển của interfaces trong Python, cũng như cách thức sử dụng protocol và ABCs sao cho hiệu quả nhất.

---
### Table of Contents

- [Chapter 11: Interfaces - From Protocols to ABCs](#chapter-11-interfaces---from-protocols-to-abcs)
  - [Table of Contents](#table-of-contents)
  - [Interfaces and Protocols in Python Culture](#interfaces-and-protocols-in-python-culture)
  - [Python Digs Sequences](#python-digs-sequences)
  - [Monkey-Patching to Implement a Protocol at Runtime](#monkey-patching-to-implement-a-protocol-at-runtime)
  - [Waterfowl and ABCs](#waterfowl-and-abcs)
  - [Subclassing an ABC](#subclassing-an-abc)
  - [ABCs in The Standard Library](#abcs-in-the-standard-library)
    - [ABCs in `collections.abc`](#abcs-in-collectionsabc)
    - [ABCs in `numbers`](#abcs-in-numbers)
  - [Defining and Using an ABC](#defining-and-using-an-abc)
    - [ABC Syntax Details](#abc-syntax-details)
    - [Subclassing The Tombola ABC](#subclassing-the-tombola-abc)
    - [A Virtual Subclass of Tombola](#a-virtual-subclass-of-tombola)
  - [Usage of register](#usage-of-register)
  - [Geese Can Behave Like Ducks](#geese-can-behave-like-ducks)
  - [Summary](#summary)
  - [Soapbox](#soapbox)
    - [Type Hints](#type-hints)
    - [Is Python Weakly Typed?](#is-python-weakly-typed)
    - [Monkey Patching](#monkey-patching)
    - [Interfaces in Java, Go, and Ruby](#interfaces-in-java-go-and-ruby)
    - [Metaphors and Idioms in Interfaces](#metaphors-and-idioms-in-interfaces)

---
### Interfaces and Protocols in Python Culture

Python vốn đã rất thành công từ trước khi ABCs xuất hiện, và phần lớn code Python hiện nay không sử dụng ABCs chút nào. Ngay từ [Chương 1](../p1-prologue/c1-the-python-data-model.md), ta đã nói về duck typing và protocol như là những interfaces không chính thức giúp ta có thể sử dụng đa hình (polymorphism) trong các ngôn ngữ lập trình kiểu động (dynamic typing) như Python.

Để có thể implement interface mà không cần từ khóa `interface` hay khi không có `ABC`, trước hết Python yêu cầu class expose ra một tập hợp các thuộc tính và phương thức public được định nghĩa bởi chính nó hoặc bởi lớp mà nó thừa kế, bao gồm cả các "magic" hay "dunder" methods (như `__len__` hay `__getitem__`). Khi đó, một interface được định nghĩa là một tập con của các phương thức public trong class mà thực hiện một nhiệm vụ cụ thể nào đó trong hệ thống.

Khi ta nói một object là "iterable", ta ám chỉ rằng nó có thể được duyệt qua bằng cách gọi đến phương thức `__iter__`, hay một object là "file-like" nếu ta có thể đọc ghi từ nó thông qua các phương thức như `read()` hay `write()`.

Protocol là interface, nhưng nó là không chính thức: Không thể ép buộc một đối tượng nào phải implement một protocol nào, chỉ có interface chính thức (`ABC`) mới có khả năng làm điều đó. Đôi khi đối tượng chỉ implement một phần của protocol, cũng chẳng sao, vì đôi khi ta chỉ cần một đối tượng "file-like" có thể được đọc qua phương thức `read()` mà chẳng cần phải ghi vào nó, tất cả đều phụ thuộc vào ngữ cảnh.

Protocol cũng không phụ thuộc vào quan hệ thừa kế, một đối tượng có thể implement nhiều protocol khác nhau để thực hiện nhiều vai trò khác nhau.

Một trong những protocol quan trọng nhất của Python là sequence protocol, và Python hỗ trợ nó rất đa dạng theo nhiều cách khác nhau, trong mục tiếp theo ta sẽ đi tìm hiểu sâu hơn về protocol này.

---
### Python Digs Sequences

Dưới đây là biểu đồ UML mô tả interface `Sequence` được định nghĩa trong `collections.abc`:

![alt text](./images/sequence-interfaces.png)

Interface chính thức `Sequence` yêu cầu người dùng phải implement kha khá phương thức cho nó. Tuy nhiên, nếu không sử dụng interface, người dùng vẫn có thể tạo ra một sequence-like object bằng một phương thức duy nhất `__getitem__`:

```python
class Foo:
    def __getitem__(self, pos):
        return range(0, 30, 10)[pos]
```

Chỉ vậy là đủ để ta có thể: (1) truy cập tới phần tử ở vị trí bất kỳ, (2) duyệt qua danh sách các phần tử của sequence và (3) kiểm tra một phần tử có nằm trong sequence hay không:

```python
>>> f = Foo()
>>> for i in f: print(i)
...
0
10
20
>>> 20 in f
True
>>> 15 in f
False
```

Ta chẳng cần implement `__iter__` để có thể duyệt qua danh sách các phần tử, bởi cú pháp `for...in` sẽ fallback về phương thức `__getitem__`, cũng chẳng cần implement `__contains__` để kiểm tra `item` có nằm trong sequence hay không, vì Python cũng fallback về kiển tra bằng cách so sánh `item` với tất cả các phần tử nằm trong sequence.

Sở dĩ ta có thể làm được điều này là vì Python đã cố gắng hết sức để biến những đối tượng chỉ có chút gì đó giống với sequence thành sequence, không phải qua interface chính thức, mà là qua protocol và duck-typing.

---
### Monkey-Patching to Implement a Protocol at Runtime

Ta bắt đầu bằng một ví dụ implement một bộ bài Tú lơ khơ sử dụng sequence protocol, ta sẽ implement thêm phương thức `__len__` để có thể đếm số lá trong bộ bài qua hàm `len()`:

```python
import collections

Card = collections.namedtuple('Card', ['rank', 'suit'])

class FrenchDeck:
    ranks = [str(n) for n in range(2, 11)] + list('JQKA')
    suits = 'spades diamonds clubs hearts'.split()

    def __init__(self):
        self._cards = [Card(rank, suit) for suit in self.suits
                       for rank in self.ranks]

    def __len__(self):
        return len(self._cards)

    def __getitem__(self, position):
        return self._cards[position]
```

Tuy nhiên, khi sử dụng class này, ta phát hiện ra là mình không thể xáo bài thông qua hàm `random.shuffle()` được vì hiện tại, `FrenchDeck` chưa hỗ trợ gán phần tử:
```python
>>> from random import shuffle
>>> deck = FrenchDeck()
>>> shuffle(deck)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/usr/lib/python3.9/random.py", line 363, in shuffle
    x[i], x[j] = x[j], x[i]
TypeError: 'FrenchDeck' object does not support item assignment
```

Để có thể xáo bài, `FrenchDeck` cần implement Mutable Sequence protocol, bằng cách định nghĩa phương thức `__setitem__`. Thay vì sửa lại mã nguồn, ta có thể cập nhật phương thức này ngay tại runtime, hành động này gọi là *monkey-patching:*

```python
>>> def set_card(deck, position, card):
...     deck._cards[position] = card
... 
>>> FrenchDeck.__setitem__ = set_card
>>> shuffle(deck)
>>> deck[:5]
[Card(rank='J', suit='hearts'), Card(rank='K', suit='hearts'), Card(rank='8', suit='clubs'), Card(rank='6', suit='diamonds'), Card(rank='Q', suit='spades')]
```

Monkey patching là một công cụ mạnh mẽ (và nguy hiểm) để lập trình viên có thể debug và live-patching hệ thống mà không cần chỉnh sửa mã nguồn. Ví dụ trên cũng cho thấy đặc tính dynamic của protocol: `random.shuffle()` không cần biết đối tượng truyền vào nó là gì, nó chỉ yêu cầu đối tượng đó phải có phương thức `__setitem__`, bất kể phương thức đó được định nghĩa ngay từ đầu hay được thêm vào sau đó thông qua monkey patching.

---
### Waterfowl and ABCs

Protocols và duck-typing là công cụ hữu hiệu để lập trình tổng quát. Một phương thức duck-typing thường không cần quan tâm đến kiểu của tham số đầu vào. Và thực tế, việc dùng quá nhiều chuỗi `if/elif/elif...` để xử lý các kiểu dữ liệu đầu vào khác nhau không được cho là biểu hiện của một thiết kế hướng đối tượng tốt. Những built-in functions như `isinstance` và `issubclass` bởi vậy không được khuyên dùng vì nó trái với triết lý lập trình đa hình.

Tuy nhiên, trong tự nhiên, có nhiều trường hợp hai loài có cùng đặc điểm di truyền do tình cờ chứ không phải do cùng chung nguồn gốc. Việc xác định tính gần gũi về mặt di truyền của hai loài vì thế phải dựa trên giám định gen chứ không phải dựa trên quan sát kiểu hình. Nói cách khác, đôi khi một con vật đi như con vịt, kêu như con vịt chưa hẳn đã là con vịt. Tương tự như vậy, việc lập trình duck-typing đôi khi cần phải đi kèm với những ràng buộc chặt chẽ hơn, nói vui là *goose-typing*. Vì lí do đó, `interface` và `ABC` classes ra đời.

Một class có thể xác định interface, hay lớp trừu tượng cha (abstract base class - ABC), cho mình bằng việc thừa kế từ chính lớp đó hoặc `register` lớp đó. Sau đó, sử dụng phương thức `isinstance` để kiểm tra đối tượng hiện tại có implements/inherits ABC đó hay không là một cách để thông báo với cliet code rằng: "Hãy implement những thứ này đi rồi hãy gọi cho tôi!". Điều này thường xảy ra khi bạn xây dựng một framework. Bên ngoài phạm vi framework, duck-typing luôn là lựa chọn đơn giản và mềm dẻo hơn.

Tóm lại:
-   Duck-typing không bao giờ dùng `isinstance` để kiểm tra kiểu của tham số, goose-typing có dùng `isinstance`, nhưng chỉ dùng cho cho các kiểu `ABC` mà thôi
-   Bạn sẽ không bao giờ phải định nghĩa `ABC` trong production code, duck-typing là đủ trong hầu hết các trường hợp. Tránh việc có trong tay một cái búa mới rồi nghĩ rằng tất cả mọi vấn đề đều là những cái đinh ("When all you have is a hammer, every problem looks like a nail")

---
### Subclassing an ABC

Dưới đây là ví dụ thiết kế một `FrenchDeck` sử dụng interface `collections.MutableSequence`:

```python
import collections

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
```

Các phương thức được implement ở trên là tối thiểu đối với một `collections.MutableSequence`, thiếu bất kỳ phương thức nào cũng sẽ tạo ra một exception `TypeError` **tại runtime**. Dưới đây là mối quan hệ giữa `Mutable Sequence` và các abstract Class khác mà nó thừa kế (các phương thức in nghiêng là abstract methods):

![alt text](./images/mutable-sequence.png)

Các phương thức không được in nghiêng là các phương thức ready-to-use ngay khi các phương thức abstract được implement, người dùng có thể sử dụng chúng mà không cần phải implement lại.

---
### ABCs in The Standard Library

Kể từ Python 2.6, ABCs trở nên có sẵn trong thư viện chuẩn. Hầu hết ABCs được định nghĩa trong module `collections.abc`, số khác trong các packages như `number`, `io`, etc.

#### ABCs in `collections.abc`

Dưới đây là biểu đồ UML các ABCs trong module `collections.abc`:

![alt text](./images/abcs.png)

-   `Iterable`, `Container`, và `Sized`: Tất cả các collection implement dựa vào interface (không dùng protocol) nên implement cả ba lớp này. `Iterable` hỗ trợ thao tác duyệt với `__iter__`, `Container` hỗ trợ toán tử `in` với phương thức `__contains__` và `Sized` hỗ trợ `len()` với phương thức `__len__`
-   `Sequence`, `Mapping` và `Set`: Đây là các kiểu immutable collections đặc trưng, mỗi loại đều có một subclass mutable tương ứng: `MutableSequence`, `MutableMapping` và `MutableSet`
-   `MappingView`: Hỗ trợ các phương thức mapping. `ItemsView` hỗ trợ `.items()`, `ValuesView` hỗ trợ `.values()`, `KeysView` hỗ trợ `.keys()`
-   `Callable`và `Hashable`: Chức năng chính là để hỗ trợ `isinstance` kiểm tra xem một object có là callable hay hashable không
-   `Iterator`: Thừa kế `Iterable`, sẽ được bàn đến ở chương 14

#### ABCs in `numbers`

Các ABCs trong package `number` có quan hệ bao chứa, các lớp sau có mức độ trừu tượng thấp hơn và chứa trong lớp dưới:

```python
Number > Complex > Real > Rational > Integral
```
Cú pháp `isinstance(x, numbers.Real)` chấp nhận x là bất kỳ kiểu nào trong số: `bool`, `int`, `float`, `fractions.Fraction` hay bất kỳ kiểu số thực nào được định nghĩa trong các thư viện ngoài như `Numpy`, `Scipy` hay `Tensorflow`.

---
### Defining and Using an ABC

Usecase phổ biến nhất để sử dụng ABC interfaces là tạo và làm việc với frameworks.

Kịch bản: Tạo một framework nhằm hỗ trợ các class mô phỏng chức năng quay số may mắn, bằng cách nạp vào các con số bất kỳ rồi trả về một số ngẫu nhiên trong số đó.

Dưới đây là mô hình interface:

![alt text](./images/tombola-interface.png)

Chú ý, các phương thức in nghiêng là abstract methods.

Trong đó `Tombola` là ABC định nghĩa ra một class có chức năng như trong yêu cầu một cách hợp lệ. các phương thức của nó là:
-   *`.load(...)`*: thêm item vào container
-   *`.pick()`*: loại bỏ một phần tử ngẫu nhiên nằm trong container và trả về nó
-   `.loaded()`: trả về True nếu như có ít nhất một item nằm trong container
-   `.inspect()`: trả về một `tuple` được sắp xếp được tạo từ các items nằm trong container mà không làm thay đổi nội dung của nó

Các class phía dưới hoặc thừa kế, hoặc sử dụng (register) ABC này.

Code của class `Tombola` như sau:

```python
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
```

*Chú ý:*
-   Sử dụng decorator `abc.abstractmethod` để định nghĩa abstract methods
-   Abstract methods thường để trống, chỉ có docstring cho phương thức
-   Phương thức `inspect` cho thấy ABC class có thể chứa phương thức thường bên cạnh abstract method, miễn là phương thức thường chỉ sử dụng các phương thức và thuộc tính nằm trong ABC class

Ví dụ một user-defined class implement `Tombola`:

```python
>>> from tombola import Tombola
>>> class Fake(Tombola): #
...     def pick(self):
...         return 13
...
>>> Fake
<class '__main__.Fake'>
<class 'abc.ABC'>, <class 'object'>)
>>> f = Fake()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: Can't instantiate abstract class Fake with abstract methods load
```

*Nhân xét:* 
-   Python biết `Fake` implement `Tombola` và không cho phép khởi tạo đối tượng từ `Fake` vì nó implement thiếu abstract method `load`.

#### ABC Syntax Details

Cú pháp sử dụng (thừa kế) một `abc.ABC` class trong các phiên bản Python khác nhau:

-   Python 2: 
    ```python
    class Tombola(object):
    __metaclass__ = abc.ABCMeta
    # ...
    ```
-   Python 3, version &lt; 3.4:
    ```python
    class Tombola(metaclass=abc.ABCMeta):
        #...
    ```
-   Python 3.4+:
    ```python
    class Tombola(abc.ABC)
    ```

Bên cạnh `@abstractmethod`, `abc` còn định nghĩa `@abstractclassmethod`, `@abstractstaticmethod` và `@abstractproperty`. Tuy nhiên, kể từ Python 3.3, chúng không còn được hỗ trợ vì sự xuất hiện của cơ chế chồng decorator. Ví dụ ta có thể tạo một abstract class method như sau:

```python
class MyABC(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def an_abstract_classmethod(cls, ...):
        pass
```
*Chú ý:*
-   `@abc.abstractmethod` là decorator nằm *dưới cùng* trên chồng decorators.

#### Subclassing The Tombola ABC

Giờ ta bắt tay vào viết các lớp cụ thể implement `Tombola`, bắt đầu bằng lớp `BingoCage` như sau:

```python
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
```

*Nhận xét:*
-   Chiến lược của `BingoCage` là xáo trước các con số tại thời điểm nạp vào và lấy chúng ra một cách lần lượt
-   `BingoCage` sử dụng lại hàm `loaded` và `inspect` định nghĩa bởi `Tombola`

Bạn có thể nhận thấy ngay rằng phương thức `inspect()` của `Tombola` được implement rất phức tạp, và `loaded()` sử dụng `inspect()` một cách thiếu hiệu quả.

Dưới đây là lớp `LotteryBlower` định nghĩa lại hai phương thức này một cách hiệu quả hơn:

```python
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
```

*Nhận xét:*
-   Chiến lược của `LotteryBlower` là nạp các số vào theo thứ tự gốc mà không cần xáo trộn, mỗi khi lấy ra một số sẽ chọn số tại vị trí ngẫu nhiên
-   `loaded()` được implement một cách đơn giản mà không phụ thuộc vào `inspect`, độ phức tạp `O(1)`
-   `inspect()` được implement chỉ bằng một dòng, tuy độ phức tạp không giảm đi - `O(nlog(n))`, do ta vẫn cần sắp xếp các con số khi lấy về

Bên cạnh việc implement abstract method, đôi khi ta cũng cần implement lại các phương thức thường khi thừa kế một abstract class để xử lý một cách hiệu quả hơn, mặc dù phương thức thường của abstract class vẫn hoạt động với mọi lớp con thừa kế (implement) nó.

#### A Virtual Subclass of Tombola

Ta có thể đăng kí một virtual subclass cho một `ABC` bằng phương thức `register` của `ABC` đó. Các virtual subclass sau đó có thể được nhận dạng bằng các phương thức `issubclass` hay `isinstance` tuy nhiên không thừa kế bất kì thuộc tính hay phương thức nào của ABC gốc cũng như về bản chất không là một lớp con của `ABC` đó.

Cú pháp đăng ký virtual subclass:
-   Python 3.4+:
    ```python
    @Tombola.register
    class TomboList(list):
    ```
-   Python 3.3-:
    ```python
    Tombola.register(TomboList))
    ```

Kiểm tra virtual subclass:
```python3
>>> issubclass(TomboList, Tombola)
True
>>>
>>> t = TomboList(range(100))
>>> isinstance(t, Tombola)
True
>>>
>>> TomboList.__mro__
(<class 'tombolist.TomboList'>, <class 'list'>, <class 'object'>)
```

*Nhận xét:*
-   `TomboList` là subclass của `Tombola` nhưng không thừa kế từ `Tombola` (không có `Tombola` trong gia phả `__mro__`)

---
### Usage of register

Do Python hỗ trợ đa kế thừa, việc ta định nghĩa một class và `register` nó là virtual subclass của một `ABC` không đem lại lợi ích gì so với việc thừa kế trực tiếp `ABC` đó, có chăng nó chỉ làm vừa lòng các developers khó tính muốn phân tách rạch ròi giữa implement và inherit mà thôi.

Cái lợi chủ yếu mà virtual subclass đem lại đó là ta có thể thông báo rằng một class nằm trên module khác là implement interface mà mình tạo ra. Ví dụ điển hình là trong `collections.abc`, nhiều kiểu built-in được register vào `Sequence` như sau:

```python
Sequence.register(tuple)
Sequence.register(str)
Sequence.register(range)
Sequence.register(memoryview)
```

Như vậy, tất cả các đối tượng `tuple`, `str`, `range` và `memoryview` đều là instance của `Sequence` mà không cần thay đổi định nghĩa của các kiểu built-in này.

---
### Geese Can Behave Like Ducks

Ta thậm chí chẳng cần dùng `register` cho một class implement `__len__` để Python biết được nó là subclass của `abc.Sized`:
```python
>>> class Struggle:
...     def __len__(self): 
...         return 23
>>> from collections import abc
>>> issubclass(Struggle, abc.Sized)
True
```

Tại sao lại thế nhỉ? Lý do là vì khi chạy hàm `issubclass(Struggle, abc.Sized)`, Python gọi sang một phương thức đặc biệt `__subclasshook__` định nghĩa trên `abc.Sized`:

```python
class Sized(metaclass=ABCMeta):
    __slots__ = ()
    
    @abstractmethod
    def __len__(self):
        return 0
    @classmethod
    def __subclasshook__(cls, C):
        if cls is Sized:
            if any("__len__" in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented
```

Chỉ cần `Struggle` implement phương thức `__len__`, `abc.Sized.__subclasshook__` sẽ trả về `True` và biểu thức `issubclass(Struggle, abc.Sized)` sẽ nhận kết quả `True`.

Có thể thấy, `__subclasshook__` đưa thêm gia vị của duck-typing vào trong ngữ cảnh của goose-typing. Bạn có thể định nghĩa một `ABC` với các abstract methods cho trước. Và một class bất kỳ, không cần thừa kế hay `register` `ABC` của bạn, vẫn có thể implement interface định nghĩa bởi `ABC` nếu class đó định nghĩa đủ các abstract methods cũng như bạn định nghĩa `__subclasshook__` cho `ABC` của mình một cách hợp lý.

Câu hỏi đặt ra là bạn có nên implement `__subclasshook__` cho `ABC` của mình hay không? Câu trả lời là không. Ngay cả trong các thư viện chuẩn, `__subclasshook__` không được dùng nhiều, vì không có nhiều mối quan hệ hiển nhiên như việc một đối tượng sở hữu phương thức `__len__` là một `abc.Sized`. Thay vì nhận vơ rằng một đối tượng sở hữu phương thức `x` implement interface `A`, hãy để người dùng tự chỉ ra điều đó trong code của họ.

---
### Summary

Nội dung chương này nhắc lại về protocol như là một interface không chính thức trong Python, sau đó đi sâu vào cách định nghĩa interface chính thức `ABC` và sử dụng nó thông qua thừa kế hoặc qua phương thức `register`. `__subclasshook__` cũng được giới thiệu như là một cách đem duck-typing vào trong ngữ cảnh của interface.

---
### Soapbox

#### Type Hints

#### Is Python Weakly Typed?

#### Monkey Patching

#### Interfaces in Java, Go, and Ruby

C++ cho phép định nghĩa interface thông qua abstract classes kể từ phiên bản 2.0 (1989). Tương tự như Python, C++ là ngôn ngữ đa kế thừa, việc dùng abstract class cho interface là có thể thực hiện được và cũng khá tự nhiên. Trái lại, Java lựa chọn thiết kế đơn kế thừa, khiến nó không thể dùng abstract class cho interface mà nó cần một cấu trúc `interface` riêng biệt. Việc dùng từ khóa `interface` một cách rõ ràng như thế có lẽ là một trong những đóng góp lớn nhất của Java cho lập trình hướng đối tượng. Kể từ Java 8, người dùng đã có thể định nghĩa các "default methods" bên cạnh abstract methods cho interface, khiến interface trong Java trở nên gần hơn với abstract class trong C++ và Python.

Golang lựa chọn một hướng đi khác hoàn toàn. Thứ nhất, trong Go không hề có khái niệm thừa kế (các nhà phát triển ngôn ngữ Go đã đưa việc thực hành "composition over inheritance" lên đến đỉnh cao bằng cách loại bỏ hẳn khái niệm kế thừa ra khỏi ngôn ngữ). Thêm nữa, người dùng không cần và cũng kông thể chỉ định một kiểu implement một interface nào trong Golang, trình biên dịch sẽ làm điều đó cho bạn. Do Go là ngôn ngữ định kiểu tĩnh (static type-checking), cơ chế này có thể tạm gọi là "static duck typing", khi mà các interfaces sẽ được kiểm tra tại thời điểm biên dịch để xem kiểu nào implement chúng.

So sánh với Python, cơ chế này trong Go giống như nếu toàn bộ các ABCs đều được implement `__subclasshook__`, giúp người dùng không bao giờ phải thừa kế hay `register` một ABC nào. Python có thể bắt chước bằng cách thực hiện kiểm tra kiểu của tất cả các tham số hàm thông qua cơ chế function annotation. Song, do type-checking hiện vẫn đang là optional trong Python, sẽ khó có khả năng điều này thực hiện được trong tương lai gần.

Lập trình viên Ruby lại là những người có niềm tin sắt đá vào duck typing, và trong Ruby không có cách chính thức nào để định nghĩa interface. Thay vào đó, cách làm của Ruby tương tự như Python trước phiên bản 2.6: `raise NotImplementedError` bên trong phương thức nếu muốn nó trở thành abstract method. Người dùng bắt buộc phải định nghĩa phương thức đó nếu muốn kế thừa từ class này.

Tuy vậy, Yukihiro “Matz” Matsumoto, nhà sáng lập Ruby, đã từng nói ngôn ngữ này sẽ phát triển theo hướng static typing. Ở thời điểm hiện tại (2014), vẫn chưa rõ Ruby sẽ thiết kế interface như thế nào khi đi theo hướng static typing: sử dụng function annotations hay phát triển các interfaces chính thức như Python đã từng làm.

Tôi tin rằng `ABC`, cùng với `register` và `__subclasshook__`, đã mang interface chính thức đến với Python mà không làm mất đi những lợi thế vốn có của dynamic typing.

Có lẽ, đây là thời điểm để những con ngỗng vượt mặt những con vịt rồi.

#### Metaphors and Idioms in Interfaces