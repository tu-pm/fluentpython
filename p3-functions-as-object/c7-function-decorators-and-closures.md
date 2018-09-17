# FluentPython-P3-C7: Function Decorators and Closures

The end goal of this chapter is to explain exactly how function decorators work, from the simplest registration decorators to the rather more complicated parametrized ones.

However, before we reach that goal we need to cover:

*   How Python evaluates decorator syntax
*   How Python decides whether a variable is local
*   Why closures exist and how they work
*   What problem is solved by nonlocal

With this grounding we can tackle further decorator topics:

*   Implementing a well-behaved decorator
*   Interesting decorators in the standard library
*   Implementing a parametrized decorator

## Decorators 101

Một decorator là một callable mà lấy tham số truyền vào là một hàm khác (hàm này gọi là decorated function). Decorator thực hiện một vài thao tác xử lý trên decorated function và trả về hàm này hoặc thay thế nó bởi một callable khác

Nói cách khác, đoạn code này:

```python
@decorate
def target():
    print('running target()')
```

Có tác dụng tương tự như:

```python
def target():
    print('running target()')

target = decorate(target)
```

Hai điểm cần lưu ý đối với decorators:

*   decorated functions sẽ bị thay thế bởi hàm mà decorator trả về
*   Thao tác thay thế decorated function được thực hiện ngay khi module được load, chứ không phải đến khi decorated function được gọi

## When Python Executes Decorators

Như đã nói, decorators được thực thi ngay khi module được import (ví dụ trang 185-186). Mặt khác, decorated functions chỉ chạy khi nó được gọi một cách trực tiếp. Đây chính là điểm khác biệt giữa *import time* và *run time*.

Thông thường, decorators được định nghĩa trong một module và có thể được sử dụng cho hàm ở module khác. Bên cạnh đó, hầu hết các decorator định nghĩa ra một inner function và trả về nó, thay vì trả về hàm ban đầu (decorated function).

***Trick:***

*   Cú pháp `'%s' % obj` có chức năng format `obj` về dạng xâu bằng cách gọi đến phương thức `__repr__` của nó

## Decorator Enhanced Strategy Pattern

Trong ví dụ tính discount ở chương 6 về strategy pattern, ta phải duy trì một danh sách các chiến lược promotion để sau đó hàm `best_promo` có thể đánh giá từng chiến lược trong danh sách này và đưa ra kết quả tốt nhất. Vấn đề nảy sinh nếu hard-code danh sách này đó là mỗi khi có người thêm một chiến lược discount mới, họ lại phải thêm nó vào danh sách một cách thủ công. Decorator giúp giải quyết vấn đề này một cách gọn gàng và đẹp mắt:

*   Bước 1: Định nghĩa decorator `promotion` có chức năng tự động thêm các chiến lược vào `promos` list:
    ```python
    promos = []
    
    def promotion(promo_func):
        promos.append(promo_func)
        return promo_func
    ```

*   Bước 2: Với mỗi chiến lược discount, ta thêm decorator `@promotion` phía trước, như vậy chúng sẽ được thêm vào `promos` mà không lo bị sót
    ```python
    @promotion
    def fidelity(order):
        ...
    
    @promotion
    def bulk_item(order):
        ...

    @promotion
    def large_order(order):
        ...
    ```

Việc làm này đem lại nhiều tác dụng:

*   Không cần quy tắc tên đặc biệt cho các hàm để chương trình có thể phân loại các hàm
*   Làm nổi bật chức năng của hàm, tăng tính khả đọc
*   Dễ dàng disable một promotion nào đó bằng việc comment decorator
*   Có thể định nghĩa chiến lược discount trong module khác, miễn là chúng sử dụng decorator `@promotion`

Như đã nói, decorator hầu như đều thay thế decorated function bằng một inner function khai báo bên trong nó. Để thực hiện được điều này, cần nắm vững về closures mà trước hết là phạm vi biến trong Python.

## Variable Scope Rules

*   Rule #1: Khi một biến được khai báo trong phạm vi của một hàm, nó mặc định là biến cục bộ. Trong trường hợp ta đã khai báo biến này bên ngoài hàm và reference đến nó bên trong hàm trước khi nó được định nghĩa lại là biến cục bộ, chương trình vẫn sẽ không chạy.

*   Rule #2: Sử dụng từ khóa `global` để khai báo biến toàn cục bên trong hàm

## Closures

Closure là một hàm được định nghĩa bên trong một hàm khác, với mục đích chủ yếu là khiến nó có thể truy cập được tới những biến không toàn cục nằm bên ngoài nó (tức là nằm trong lớp chứa nó).

Xét một ví dụ: Hãy định nghĩa một callable `avg` sao cho mỗi lần gọi `avg(i)` với i là một số, nó sẽ trả về trung bình cộng của tất cả tham số đã truyền vào nó từ trước đến giờ.

*   Cách 1: `avg` một object có lưu một attribute là một sequence và được implement phương thức `__call__` thực hiện yêu cầu đề bài:

    ```python
    def Averager(object):
        def __init__(self):
            self.series = []
        
        def __call__(self, new_value):
            self.series.append(new_value)
            return sum(series) / len(series)
    ```
*   Cách 2: Sử dụng function

    ```python
    def make_averager():
        series = []

        def averager(new_value):
            series.append(new_value)
            return sum(series) / len(series)
        
        return averager
    ...

    >>> avg = make_averager()
    >>> avg(10)
    10
    >>> avg(11)
    10.5
    >>> avg(12)
    11
    ```

Điểm đặc biệt ở cách thứ hai đó là biến `series`. Đối với `make_avarager` nó là biến cục bộ, tức là nó đã được giải phóng khi hàm này trả về hàm `avarager`. Vậy thì tại sao `avarager` vẫn có thể tiếp tục truy cập vào biến này sau khi `make_avarager` đã return?

Câu trả lời là Python đã lưu lại các biến cục bộ khai báo bởi `make_avarager` mà được sử dụng bởi `avarager`, ở đây chính là `series`. Tên gọi của loại biến này là *free variable* hay biến tự do, ta có thể xem danh sách các biến tự do của `avarager` bằng cú pháp:

```python
>>> avg.__code__.co_freevars
('series',)
```

To summarize: a closure is function that retains the bindings of the free variables that exist when the function is defined, so that they can be used later when the function is invoked and the defining scope is no longer available.

## The nonlocal Declaration

Chắc hẳn bạn đã để ý rằng cách tính trung bình trong ví dụ trên là không thuận tiện, ta chỉ cần lưu giá trị tổng hiện thời và số lượng giá trị đã truyền vào thôi:

```python
def make_avarager():
    count = 0
    total = 0

    def avarager(new_value):
        count += 1
        total += new_value
        return total / count

    return avarager
```

Tuy nhiên, code này sẽ không chạy được. Lý do là bởi ta đã thực hiện gán giá trị cho `count` và `total` trong `avarager` và biến nó thành biến cục bộ. Với giải pháp dùng `series` ta không thực hiện phép gán nào với nó cả, vì thế nó vẫn là biến tự do, nhưng ở đây thì khác.

Để khắc phục điều này, nếu như bạn có ý định gán giá trị cho một biến tự do mà không muốn nó trở thành biến cục bộ, hãy dùng từ khoá **nonlocal**:

```python
    def make_averager():
        count = 0
        total = 0
    def averager(new_value):
        nonlocal count, total
        count += 1
        total += new_value
        return total / count
    return averager
``` 

## Implementing a Simple Decorator

Dưới đây là một ví dụ về decorator trả về thời gian tính toán của decorated function:

```python
import time

def clock(func):
    def clocked(*args):
        t0 = time.time()
        result = func(*args)
        elapsed = time.time() - t0
        print('Took %s seconds' % elapsed)
        return result
    return clocked
```

Tuy nhiên, ví dụ này có nhược điểm là nó không hỗ trợ hàm có keyword arguments và khi decorated function bị thay thế bởi decorator inner function, các thuộc tính `__name__` và `__doc__` của nó cũng bị thay đổi theo (tác dụng phụ không mong muốn). Để giải quyết vấn đề này, hãy sử dụng decorator `functools.wraps` cho chính inner function:

```python
import time
import functools

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
def add(x, y):
    return x + y
```

Tại sao lại truyền `func` vào cú pháp `@functools.wraps(func)`? Câu trả lời là `wraps` cần biết về decorated function để giữ lại tên và doc của nó. Dưới đây là mô tả cách thức python xử lý đoạn mã trên:

1.  Tại thời điểm load module, hàm `add` được thay đổi bởi decorator `clock2`:
    ```python
    add = clock2(add)
    ```
2.  Do `clock2` trả về `clocked` nên `add` được gán bằng `clocked`
3.  `clocked` cũng là một decorated function, vậy nên nó cũng bị thay đổi tại import time:
    ```python
    clocked = functools.wraps(func)(clocked)
    ```
4.  Vọc vạch đoạn mã nguồn của `functools.wraps` ta thấy nó nhận một positional argument là decorated function (`func`) và trả về cú pháp:
    ```python
    return partial(update_wrapper, wrapped=wrapped, ...)
    ```
5.  Tiếp tục quan sát `functools.update_wrapper`, ta thấy nó nhận hai positional arguments là decorator (wrapper) và decorated funcion(wrapped). Hàm này thực hiện gán các thuộc tính như `__doc__` hay `__name__` của wrapped cho wrapper.

Như vậy quá trình biến đổi `clocked` diễn ra như sau:

    ```python
    clocked = functools.wraps(func)(clocked) = functools.partial(functools.update_wrapper, func)(clocked) = functools.updatewrapper(func, clocked)
    ```

Đây chính là design pattern để implement một decorator có tham số.

## Decorator in The Standard Library

Python có 3 built-in functions được thiết kế để decorate các methods: `@property`, `@classmethod` và `@staticmethod`. Ý nghĩa và cách sử dụng các decorator này sẽ được đề cập đến sau trong phần lập trình hướng đối tượng với Python.

Bên cạnh đó, Python còn hỗ trợ rất nhiều decorator hữu ích trong các công việc khác nhau, dưới đây là 3 trong số đó:

*   `functools.wraps`: Thiết kế well-behaved decorators, đã sử dụng ở trên
*   `functools.lru_cache`
*   `functools.single_dispatch`

### Memoization with functools.lru_cache

`functools.lr_cache` là một công cụ implement các kĩ thuật tối ưu giúp lưu lại kết quả của các lần gọi kế trước của một hàm, tránh việc tính toán lại các phép tính đã được tính rồi gây tốn kém tài nguyên.

Một ví dụ đơn giản của việc trùng lặp tính toán đó là kỹ thuật tính dãy Fibonacci đệ quy không tối ưu:

```python

@clock
def fibonacci(n):
    return n if 2 > n else fibonacci(n-2) + fibonacci(n-1)
```

Thử tính `fibonacci(5)` và đây là kết quả:

```bash
>>> fibonacci(5)
[0.00000262s] fibonacci(1) -> 1 
[0.00000262s] fibonacci(0) -> 0 
[0.00016236s] fibonacci(2) -> 1 
[0.00000334s] fibonacci(1) -> 1 
[0.00026298s] fibonacci(3) -> 2 
[0.00000262s] fibonacci(1) -> 1 
[0.00000286s] fibonacci(0) -> 0 
[0.00009108s] fibonacci(2) -> 1 
[0.00043821s] fibonacci(4) -> 3 
[0.00000215s] fibonacci(1) -> 1 
[0.00000262s] fibonacci(0) -> 0 
[0.00008202s] fibonacci(2) -> 1 
[0.00000262s] fibonacci(1) -> 1 
[0.00016022s] fibonacci(3) -> 2 
[0.00068569s] fibonacci(5) -> 5 
5
```

Hiện tượng bùng nổ tổ hợp sẽ khiến đoạn code này sẽ không thể hội tụ với n đủ lớn, vậy cần giải quyết vấn đề này như thế nào? Đối với các ngôn ngữ khác, như C chẳng hạn, giải pháp thường gặp là lưu trữ các giá trị fibonacci vào một mảng fib[] và sử dụng lại các phần tử của mảng này để tính toán giá trị fibonacci mới hơn. Còn đối với Python? `lru_cache` chính là giải pháp:

```python
@functools.lru_cache()
@clock
def optimized_fibonacci(n):
	return n if 2 > n else optimized_fibonacci(n-1) + optimized_fibonacci(n-2)
```

Kết quả như sau:

```bash
>>> optimized_fibonacci(20)
[0.00000119s] optimized_fibonacci(1) -> 1 
[0.00000191s] optimized_fibonacci(0) -> 0 
[0.00008249s] optimized_fibonacci(2) -> 1 
[0.00010467s] optimized_fibonacci(3) -> 2 
[0.00012565s] optimized_fibonacci(4) -> 3 
[0.00014615s] optimized_fibonacci(5) -> 5 
[0.00016761s] optimized_fibonacci(6) -> 8 
[0.00018549s] optimized_fibonacci(7) -> 13 
[0.00020289s] optimized_fibonacci(8) -> 21 
[0.00021958s] optimized_fibonacci(9) -> 34 
[0.00023675s] optimized_fibonacci(10) -> 55 
[0.00025296s] optimized_fibonacci(11) -> 89 
[0.00027013s] optimized_fibonacci(12) -> 144 
[0.00028706s] optimized_fibonacci(13) -> 233 
[0.00030708s] optimized_fibonacci(14) -> 377 
[0.00032592s] optimized_fibonacci(15) -> 610 
[0.00034380s] optimized_fibonacci(16) -> 987 
[0.00036073s] optimized_fibonacci(17) -> 1597 
[0.00037718s] optimized_fibonacci(18) -> 2584 
[0.00039363s] optimized_fibonacci(19) -> 4181 
[0.00041294s] optimized_fibonacci(20) -> 6765 
6765
```

Không có một phép tính nào bị lặp lại!

Chú ý rằng, `lru_cache()` là một decorator có tham số, cú pháp đầy đủ của nó như sau:

```python
@functools.lru_cache(maxsize=128, typed=False)
```

Trong đó `maxsize` là số kết quả được lưu trữ tối đa, khi kích thước cache đầy, các bản ghi ít được sử dụng nhất gần đây sẽ  bị loại bỏ (hence: LRU - Least Recently Used). `typed` được đặt là `True` nếu muốn lưu trữ các kết quả có kiểu khác nhau tách biệt nhau.

### Generic functions with singledispatch

Python không hỗ trợ function overloading (bởi vì nó không định kiểu dữ liệu cho tham số của hàm), đây là một điểm yếu lớn khiến cho việc lập trình tổng quát (generic programming) đối với Python không được thuận tiện như C++ hay Java.

`functools.singledispatch` là công cụ giúp khắc phục điều này. Although it's not nearly simple and convenient as in other programming languages but it's the best and the prettiest they can do.

Xét một ví dụ sau: Yêu cầu chuyển đổi một python object bất kì thành một thẻ html, code của ta gần giống như sau:

```python
import html

def htmlize(obj):
    content = html.escape(repr(obj))
    return '<pre>{}</pre>'.format(content)
```

*Chú thích:* Hàm `html.escape()` biến một xâu thành một xâu an toàn để hiển thị với HTML (chuyển `'>'` -> `'&gt;'`, `' '` -> `'&nbsp;'`, ...)

Bây giờ, thay đổi yêu cầu một chút, với các kiểu dữ liệu khác nhau ta cần có các cách hiển thị khác nhau:
*   `str`: thay '\n' thành '`<br>`\n', dùng thẻ `<p>` thay vì `<pre>`
*   `int`: hiển thị dạng thập phân và thập lục phân của số
*   `list`: hiển thị dưới dạng HTML list, mỗi item được format theo kiểu của nó.

Đối với Java hay C++, ta có thể dễ dàng thay đổi bằng cách overload hàm `htmlize` với các chữ ký khác nhau. Ta không thể làm vậy trong Python mà cần dùng `functools.singledispatch` như sau:

```python
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
```

Bạn có thể hiểu được các thức hoạt động của `@singledispatch` chỉ bằng việc đọc qua đoạn code này. Dưới đây là một vài chú ý:

*   Tên của các overloading functions từ `htmlize` không quan trọng, hãy dùng ký hiệu `_` để thể hiện điều đó
*   `number.Integral` là lớp bao của `int`, tương tự `abc.MutableSequence` là lớp bao của `list`. Bạn hoàn toàn có thể dùng `int` và `list` thay vào đó, tuy nhiên cách dùng đầu tiên có khả năng tương thích đa dạng hơn (ví dụ như `int8`, `int32` hay `int64` trong `numpy` là các cách mô tả kiểu `int` với số lượng bit khác nhau, về bản chất chúng khác `int` nhưng đều là `number.Integral`)
*   Nếu bạn muốn implement một overloading function cho nhiều kiểu dữ liệu khác nhau, chồng các register decorator lên nhau như ở ví dụ cuối

## Stacked Decorators

You already knew about it.

## Parameterized Decorators

You also knew about it, but we'll get into it more specifically.

Thông thường, decorator sẽ nhận vào decorated function là tham số, vậy làm thế nào để khiến nó nhận thêm tham số khác? Câu trả lời là tạo ra một decorator trả về một decorator. Decorator nằm ngoài sẽ nhận vào các tham số, trong khi decorator phía trong nhận vào function. Ví dụ:

```python
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
```

Dưới đây là kết quả:

```bash
>>> add(3, 4)
The outer decorator took 5 arguments
7
```

Quá trình biến đổi `func` diễn ra như sau:

```python
func = outerdeco(*decoargs)(innerdeco(func)) = innerdeco(func) = innerfunc
```

Thông thường `*decoargs` là các cờ điều khiển quá trình hoạt động trong `innerfunc`, hoặc cũng có thể định nghĩa ra nhiều `innerdeco` và dùng `*decoargs` để điều khiển chọn ra `innerdeco` nào được chọn để trả về. Cách thứ nhất đơn giản, và nhất quán hơn.

## Summary Contents

We covered a lot of ground in this chapter, but I tried to make the journey as smooth as possible even if the terrain is rugged. After all, we did enter the realm of metaprogramming.

Registration decorators, though simple in essence, have real applications in advanced Python frameworks. We applied the registration idea to an improvement of our Strategy design pattern refactoring from Chapter 6.

Parametrized decorators almost aways involve at least two nested functions, maybe
more if you want to use `@functools.wraps` to produce a decorator that provides better support for more advanced techniques. One such technique is stacked decorators, which we briefly covered.

We also visited two awesome function decorators provided in the `functools` module of standard library: `@lru_cache()` and `@singledispatch`.

Understanding how decorators actually work required covering the difference between import time and run time, then diving into variable scoping, closures, and the new `nonlocal` declaration. Mastering closures and `nonlocal` is valuable not only to build decorators, but also to code event-oriented programs for GUIs or asynchronous I/O with callbacks.

## Pythonic Programming Tricks

*   Cú pháp `'%s' % obj` có chức năng format `obj` về dạng xâu bằng cách gọi đến phương thức `__repr__` của nó
*   Dùng từ khóa `nonlocal` giúp biến không bị biến thành cục bộ khi gán dữ liệu cho nó bên trong hàm
*   `functools.wraps` tạo ra well-behaved decorators
*   `functools.lru_cache` lưu trữ các phép tính đã thực hiện trước đó, tránh việc tính toán lại một phép tính thừa
*   `functools.singledispatch` cung cấp cách thức overloading methods và functions trong Python
*   Module `html` giúp chuyển đổi xâu thường thành xâu html và ngược lại
*   `locals()` trả về một `dict` các biến cục bộ trong module/class/function

