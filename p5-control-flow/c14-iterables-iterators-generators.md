op# Iterables, Iterators and Generators

## Overview

Iteration là khái niệm cơ bản trong xử lý dữ liệu. Khi mà dataset trở nên quá lớn để truyền vào bộ nhớ, ta cần phải đọc từng item một từ dataset và chỉ đọc khi được yêu cầu.

Key word `yeild` là từ khóa giúp khởi tạo ra generators, hay chính là các iterators. Theo định nghĩa, tất cả các generators đều là iterator, điểm khác biệt là iterators có chức năng *lấy* items từ một tập hợp có trước, trong khi generator *tạo ra* các items "từ không khí" (out of thin air). Tuy nhiên, trong hầu hết các trường hợp, cộng đồng Python đều coi như generators và iterators là đồng nghĩa.

Tất cả collection trong Python đều là iterable, và các iterators được dùng để hỗ trợ cho các thao tác:

*   Lặp với `for`
*   Khởi tạo và mở rộng các collections
*   Duyệt text files theo dòng
*   `list`, `dict` và `set` comprehensions
*   `tuple` unpacking
*   unpack tham số truyền vào hàm với toán tử `*`

## Sentence Class Example

Ta sẽ implement một class `Sentence` là một sequence của các `words`.

### Using Sequence Protocol

Dưới đây là đoạn code Python định nghĩa lớp `Sentence` sử dụng sequence protocol:

```python
import re
import reprlib

RE_WORD = re.compile('\w+')


class Sentence(object):

	def __init__(self, text):
		self.text = text
		self.words = RE_WORD.findall(text)

	def __getitem__(self, index):
		return self.words[index]

	def __len__(self):
		return len(self.words)

	def __repr__(self):
		return 'Sentence(%s)' % reprlib.repr(self.text)
```

*Chú ý:*

*   `re` là công cụ giúp thao tác với regular expressions của Python
    *   `\w` tương đương với `[a-zA-Z0-9_]`
    *   `re.compile(str)`: tạo ra đối tượng lưu trữ pattern là xâu được truyền vào
    *   `RE_WORD.findall(text)`: trả về danh sách các kết quả thỏa mãn pattern lưu bởi `RE_WORD` không giẫm lên nhau trong xâu `text`

*   Sequence protocol yêu cầu implement cả `__getitem__` và `__len__`, nhưng để tạo ra iterators thì chỉ cần `__getitem__`

Giờ ta có thể sử dụng Sentence như là một sequence:

```python
>>> sentence = Sentence('"The time has come," the Walrus said,')
>>> for word in sentence:
...     print(word)
... 
The
time
has
come
the
Walrus
said
>>> x, y, z, *_ = sentence
>>> x, y, z
('The', 'time', 'has')
>>> list(sentence)
['The', 'time', 'has', 'come', 'the', 'Walrus', 'said']
>>> print(*sentence, sep=', ')
The, time, has, come, the, Walrus, said
```
#### The iter Function

Mỗi khi trình thông dịch cần duyệt qua một object `x`, nó sẽ gọi hàm `iter(x)`. Hàm này thực hiện các thao tác sau:

*   Kiểm tra xem đối tượng có implement `__iter__` không, nếu có thì gọi đến phương thức đó để lấy về một iterator
*   Nếu `__iter__` không được implement nhưng `__getitem__` có, Python tạo ra một iterator và đọc từng item của object một cách lần lượt, bắt đầu từ 0
*   Trường hợp còn lại, raise `TypeError`, báo rằng đối tượng không là iterable

Bởi vì sequence được implement `__getitem__` nên chúng đều là iterable. Thực tế, các standard sequence implement `__iter__` và bạn cũng nên làm điều đó. Việc fallback về `__getitem__` chỉ để phục vụ tương thích ngược và tính năng này có thể không còn trong các phiên bản Python tương lai.

Ở đây xảy ra một hiện tượng "duck typing" điển hình: Nếu có thể gọi `iter()` trên một đối tượng, đối tượng đó là iterable, bất chấp việc có thể nó không được implement phương thức `__iter__`. Nếu muốn ràng buộc chặt chẽ đối tượng phải được implement `__iter__`, hãy dùng cú pháp "goose typing":

```python
>>> issubclass(Sentence, abc.Iterable)
False
```
Tuy nhiên, cách làm tốt nhất vẫn là sử dụng khối `try...except` để bắt `TypeError` khi không thể gọi `iter()` trên đối tượng.

### Iterables vs Iterators

*   Iterator là đối tượng được dùng để duyệt qua một collection
*   Iterable là đối tượng có thể được dùng trong phương thức `iter`, trả về một *iterator*

`str` cũng là iterable, dưới đây là cú pháp duyệt qua một xâu:

```python
s = 'ABC'
for char in s:
        print(char)
```

Cú pháp này được dịch sang thành:

```python
s = 'ABC'
it = iter(s)
while True:
    try:
        print(next(it))
    except StopIteration:
        del it
        break
```

Hàm `next()` được sử dụng để lấy phần tử tiếp theo được sinh ra bởi iterator, nếu không còn phần tử nào nữa, ngoại lệ `StopIteration` sẽ được tung ra.

Dưới đây là biểu đồ UML cho mối quan hệ giữa Iterator và Iterable standard interface trong `collection.abc`:

![images/iterator-vs-iterable.png](images/iterator-vs-iterable.png)

*Chú ý*: `__iter__` của một iterator trả lại chính nó.

Bởi vì chỉ có `__next__` và `__iter__` là hai phương thức bắt buộc đối với iterator nên ta không có cách nào để kiểm tra xem có bao nhiêu phần tử còn lại cũng như không thể reset một iterator (ngoài việc sinh gọi lại hàm iter(...).

Tóm lại, ta có định nghĩa của iterator:

*"Iterator là bất kỳ đối tượng nào được impelent phương thức `__next__` không chứa tham số mà trả về phần tử tiếp theo của một chuỗi hoặc tung ngoại lệ `StopIteration` khi không còn phần tử nào khác. Python iterator cũng là iterable vì nó được implement phương thức `__iter__` trả về chính nó."* 

### Using A Classic Iterator

Bây giờ, ta hãy implement một iterator chuẩn cho class Sentence:

```python
class Sentence:
    ...
    def __iter__(self):
        return SentenceIterator(self.words)

class SentenceIterator:

    def __init__(self, words):
        self.words = words
        self.index = 0

    def __next__(self):
        try:
            word = self.words[self.index]
        except IndexError:
            raise StopIteration()
        self.index += 1
        return word

    def __iter__(self):
        return self
```

*Chú ý:* Bắt ngoại lệ ngay khi nó có thể được sinh ra (như ví dụ trên) giúp quản lý code dễ hơn

#### Do NOT Make An Iterator From A Sequence

Không nên biến một Sequence thành một Iterator. Bạn có thể implement `__next__` cho `Sentence` và giúp nó tự duyệt qua chính nó, nhưng đây hoàn toàn không phải là một ý tưởng hay.

Theo định nghĩa, Iterator design pattern được dùng để:

*   Truy cập đến nội dung của một đối tượng mà không để lộ trạng thái biểu diễn bên trong của nó
*   Hỗ trợ nhiều yêu cầu duyệt nội dung một đối tượng một cách đồng thời
*   Cung cấp một interface thống nhất để duyệt qua các đối tượng có nhiều cấu trúc khác nhau

Dễ thấy, việc biến sequence thành iterator phá hỏng cả ba mục đích trên. Đó là lí do cần phải tạo ra một iterator riêng cho class.

### Using A Generator Function

Cách Pythonic nhất để lấy ra một iterator từ một iterable đó là biến phương thức `__iter__` thành một generator function. Dưới đây là ví dụ với lớp `Sentence`:

```python
class Sentence:
    ...
    def __iter__(self):
        for word in self.words:
            yield word
```

Bằng cách này ta không cần bắt ngoại lệ `StopIteration`, cũng không phải định nghĩa lớp `SentenceIterator` nữa.

Tất nhiên ta cũng có thể làm đơn giản hơn với cú pháp `iter(self.words)`, tuy nhiên ở đây tác giả dùng generator để lấy ví dụ giới thiệu tính năng này.

#### How Generator Functions Work

Bất kỳ một hàm nào trong Python mà có từ khóa `yield` ở thân hàm đều là một generator function - trả về một generator object khi được gọi. Nói cách khác, một generator function là một generator factory. Ví dụ:

```python
>>> def gen_123():
...     yield 1
...     yield 2
...     yield 3
... 
>>> gen_123
<function gen_123 at 0x7f91e22d5ea0>
>>> gen_123()
<generator object gen_123 at 0x7f91e0361a98>
>>> g = gen_123()
>>> print(next(g) for _ in range(3))
<generator object <genexpr> at 0x7f91dcbafe08>
>>> next(g)
1
>>> next(g)
2
>>> next(g)
3
>>> next(g)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
```

Generator function tạo ra một generator object chứa nội dung của hàm. Khi gọi `next(...)` trên generator object, hàm sẽ được thực thi cho đến khi gặp lệnh yield tiếp theo, sau đó `next(...)` trả về giá trị tính toán được ở lệnh `yield` đồng thời ngừng quá trình thực thi của hàm. Sau cùng, khi không còn lệnh `yield` nào nữa và hàm đã `return`, generator object sẽ tung ngoại lệ `StopIteration` chiếu theo `Iterator` protocol.

*Lời bình, nguyên văn:* "I find it helpful to be strict when talking about the results obtained from a generator: I say that a generator *yields* or *produces* values. But it’s confusing to say a generator *returns* values. Functions return values. Calling a generator function returns a generator. A generator yields or produces values. A generator doesn’t *return* values in the usual way: the return statement in the body of a generator function causes `StopIteration` to be raised by the generator object."

Chú ý, ta cũng có thể dùng vòng lặp `for...in` duyệt qua generator, tuy nhiên có một điểm khác thường khi duyệt qua generator so với khi duyệt qua các collections:

```python
>>> g = gen_123()
>>> for i in g:
...     print(i)
... 
1
2
3
>>> next(g)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
```
Ta đã biết Python dịch vòng lặp `for...in` thành vòng lặp `while` sử dụng con chạy là `it=iter(obj)`. Và nếu chạy lệnh `iter(generator)` thì iterator trả về chính là generator đó, bởi vì generator cũng chính là iterator. Do vậy ta không thể duyệt qua một generator hai lần.

### Using A Lazy Implementation

`Iterator` interface được thiết kế để trở nên đơn giản (*lazy*): `next(my_iterator)` cho ra một item mỗi lần gọi. Trái ngược với khái niệm đơn giản là "cồng kềnh"(*eager*). Hai khái niệm này là những khái niệm kĩ thuật quan trọng trong lý thuyết lập trình.

Class `Sentence` hiện tại vẫn chưa được *lazy*. Phương thức `__init__` phải tạo mới cả một list gồm các chữ cái và gắn nó với thuộc tính `words`. List này có độ dài tương đương cả text ban đầu. Việc làm này sẽ thực sự là thừa thãi nếu người dùng chỉ duyệt qua một vài phần tử đầu tiên của chuỗi.

Whenever you are using Python 3 and start wondering “Is there a lazy way of doing
this?”, often the answer is “Yes”.

Hàm `re.finditer` là một lazy version của `re.findall`. Thay vì trả về một list, nó trả về một generator tạo ra các `re.MatchObject` instances khi được yêu cầu. Nếu có nhiều kết quả khớp, `re.finditer` sẽ giúp tiết kiệm được rất nhiều bộ nhớ. Áp dụng nó sẽ khiến cho class `Sentence` trở nên *lazy*:

```python
class Sentence:

    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return 'Sequence (%s)' % reprlib.repr(self.text)

    def __iter__(self):
        for match in RE_WORD.finditer(self.text):
            yield match.group()

```

*Chú ý:* Phương thức `match.group()` lấy ra nội dung text được so khớp trong đối tượng `MatchObject`.

Ta vẫn còn có thể làm cho `Sentence` đơn giản hơn với generator expression

### Using Generator Expression

Generator expressions có thể được sử dụng để thay thế cho những generator functions đơn giản. Nó được hiểu là phiên bản *lazy* của list comprehension: trả về từng phần tử một mà không phải tạo ra cả một list. Nói cách khác, list comprehension là *factory* của lists, generator expression là *factory* của generators.

```python
    def __iter__(self):
        return (match.group() for match in RE_WORD.finditer(self.text))
```

#### Generator Expressions Usecases

Ưu điểm:

*   Tiết kiệm bộ nhớ hơn list comprehensions
*   Gọn gàng hơn generator functions
*   Tính khả đọc cao

Khi nào ưu tiên dùng generator function hơn:

*   Khi logic xử lý để tạo generator phức tạp hơn một dòng (logical line)
*   Khi cần sử dụng lại (vì functions có tên, expressions thì không)

## Arithmetic Progression Generator Example

Không chỉ có tác dụng lấy dữ liệu từ một collection, iterators còn có chức năng tạo ra từng phần tử một cách tại chỗ. Ví dụ, hàm `range()` trả về một cấp số cộng nguyên giới hạn, hàm `itertools.count` tạo ra một cấp số cộng không giới hạn.

Giờ ta sẽ tạo ra một lớp cấp số cộng `ArithmeticProgression`, chữ ký của nó là `ArithmeticProgression(begin, step[ ,end])`, tựa như `range(start, stop[ ,step])` nhưng khác là class của ta cho phần tử cuối là optional và step là bắt buộc.

```python
class ArithmeticProgression:

    def __init__(self, begin, step, end=None):
        self.begin = begin
        self.step = step
        self.end = end      # None -> infinite series

    def __iter__(self):
        result = type(self.begin + self.step)(self.begin) #1
        forever = self.end is None
        index = 0
        while forever or result < self.end:
            yield result
            index += 1
            result = self.begin + self.step * index #2
```

*Chú ý*:

*   #1: Kiểu của `result` là kiểu lớn hơn giữa `begin` và `step`. `result` được khởi tạo bằng `begin`
*   #2: Thay vì cộng thêm `step` tại mỗi bước cho `result`, ta tính trực tiếp từ `begin` và `step` để tránh sai số cộng dồn đối với kiểu số thực

Ví dụ sử dụng:

```python
>>> ap = ArithmeticProgression(0, 1, 3)
>>> list(ap)
[0, 1, 2]
>>> ap = ArithmeticProgression(1, .5, 3)
>>> list(ap)
[1.0, 1.5, 2.0, 2.5]
>>> ap = ArithmeticProgression(0, 1/3, 1)
>>> list(ap)
[0.0, 0.3333333333333333, 0.6666666666666666]
>>> from fractions import Fraction
>>> ap = ArithmeticProgression(0, Fraction(1, 3), 1)
>>> list(ap)
[Fraction(0, 1), Fraction(1, 3), Fraction(2, 3)]
>>> from decimal import Decimal
>>> ap = ArithmeticProgression(0, Decimal('.1'), .3)
>>> list(ap)
[Decimal('0.0'), Decimal('0.1'), Decimal('0.2')]
```

Ta có thể viết lại lớp này dưới dạng một hàm đơn giản hơn:

```python
def aritprog_gen(begin, step, end=None):
    result = type(begin+step)(begin)
    forever = end is None
    index = 0
    while forever or end > result:
        yield result
        index += 1
        result = begin + step * index
```

### Arithmetic Progression with itertools

Module `itertools` (Functions creating iterators for efficient looping) trong Python 3.4 có 19 generator functions có thể kết hợp với nhau một cách thú vị. Danh sách đầy đủ nằm ở [đây](https://docs.python.org/3.6/library/itertools.html), dưới đây là một vài ví dụ:

*   `itertools.count(start, step)`: Tạo một biến đếm chạy đến vô cùng
*   `itertools.takewhile(condition, other_generator)`: Chạy `other_generator` cho đến khi `condition` đạt `False`
*   Kết hợp hai công cụ này để viết hàm cấp số cộng:
    ```python
    def aritprog_gen(begin, step, end=None):
        first = type(begin + step)(begin)
        ap_gen = itertools.count(first, step)
        if end is not None:
            ap_gen = itertools.takewhile(lambda n: n < end, ap_gen)
        return ap_gen
    ```

## Generator Functions in The Standard Library

Bộ thư viện chuẩn của Python chứa rất nhiều generators hữu dụng:

*   Phương thức `readline` cho file objects đọc từng dòng của file
*   Hàm `os.walk` yields tên file khi duyệt qua một cây thư mục, giúp cho việc tìm kiếm trên cây thư mục trở nên dễ dàng với vòng lặp for

*Filtering generator functions:*

*   `itertools.compress(it, selector_it)`: yields items của `it` nếu như item tương ứng của `selector_it` là "đúng"
*   `itertools.dropwhile(predicate, it)`: lọc ra các phần tử liên tục đầu tiên mà `predicate` đạt `True`, in ra các phần tử còn lại
    ```python
    >>> list(dropwhile(lambda x: 5 > x, [1, 4, 6, 4, 1]))
    [6, 4, 1]
    ```
*   `filter(predicate, it)`: yields item của `it` nếu `predicate` tại `item` đạt `True`
*   `itertools.filterfalse`: ngược lại với `filter`
*   `itertools.islice`: Iterator slicing, tương tự như list slicing
*   `itertools.takewhile`: Ví dụ ở trên

*Mapping generator functions:*

*   `itertools.accumulate(it, [func])`: yields tổng của n số hạng đầu tiên trong `func(it)`
    ```python
    >>> list(itertools.accumulate([1, 2, 3, 4]))
    [1, 3, 6, 10]
    ```
*   `enumerate(iterable, start=0)`: yields các tuple đôi `(index, item)` từ `iterable`, trong đó index đánh số từ `start`
*   `map(func, it1[, it2, ..., itN])`: Tính `func` trên tham số là các phần tử đọc vào từ cả `it`, yield kết quả
*   `itertools.starmap(func, it)`: Dùng thay `map` nếu `it = zip(it1, it2, ...itN)`

*Generator functions that merge multiple input iterables*

*   `itertools.chain(it1, ..., itN)`: yields tất cả các item từ các `it` nối đuôi nhau
*   `itertools.product(it1, ..., itN)`: yields tích Đề các của các `it` đầu vào
*   `zip(it1, ..., itN)`: zip các itertors
*   `itertools.zip_longest(it1, .., itN, fillvalue=None)`: Tương tự `zip`, nhưng mà zip theo chuỗi dài nhất, các chuỗi ngắn hơn sẽ được tự động điền thêm `fillvalue`

*Generator functions that expand each input item into multiple output items*

*   `itertools.combinations(it, out_len)`: yields các tổ hợp độ dài `out_len` của các phần tử nằm trong `it`
*   `itertools.combinations_with_replacement(it, out_len)`: yields tất cả các tổ hợp lặp độ dài `out_len` của các phần tử nằm trong `it`
*   `itertools.permutations(it, out_len=None)`: yields các chỉnh hợp độ dài `out_len` của các phần tử nằm trong `it`
*   `itertools.count`: Tạo ra biến đếm đến vô cực
*   `itertools.cycle(it)`: yields các phần tử của it từ đầu tới cuối rồi lặp lại vô hạn lần
*   `itertools.repeat(item[, times])`: yields một phần tử vô hạn lần, hoặc đến số lần bằng `times`

*Rearranging generator functions*

*   `itertools.groupby(it, key=None)`: yields các tuple kép `(key, group)`, các phần tử có cùng `key` thì thuộc cùng `group` và `group` cũng là generator yields từng phần tử của nó
*   `reversed(seq)`: yields từng phần tử của sequence theo thứ tự ngược lại
*   `itertools.tee(it, n=2)`: tạo ra tuple của n generator cùng duyệt qua `it`

## The yield from Syntax

Từ Python 3.4, cú pháp:

```python
for i in iterable:
    yield i
```
có thể được thay thế bằng một statement duy nhất:

```python
yield from iterable
```
Không chỉ là cách để đơn giản hóa cú pháp cho generator functions, `yield from` còn đóng vai trò quan trọng trong lập trình *coroutine* sexddwowjc bàn tới trong chương 16.

## Iterable Reducing Functions

Các hàm trả về một giá trị duy nhất từ iterable, đã đề cập đến trong chương 5, bao gồm: `all`, `any`, `max`, `min`, `sum`, `reduce`.

Hàm `sorted` trả về list gồm các phần tử đã sắp xếp của một iterable, không trả về generators.

## A Closer Look at The iter Function

`iter()` trả về iterator từ một sequence, ta đã biết điều đó. Tuy nhiên có một usecase khác của nó, đó là trả về iterator từ bất kỳ một callable object nào. Cú pháp của nó là:

    iter(callable, sentinel) -> iterator

Tức là nó sẽ thực hiện gọi `callable` liên tục cho đến khi `callable` trả về giá trị `sentinel`

