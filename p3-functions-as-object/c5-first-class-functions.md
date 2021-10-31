## Chapter 5: First Class Functions

Mục tiêu chinh của chương này là tìm hiểu về bản chất first-class của hàm trong Python. First-class function nghĩa là hàm có thể coi như là đối tượng có thể được gán cho biến, truyền vào tham số của hàm khác, lưu trữ trong các cấu trúc dữ liệu, truy cập các thuộc tính hàm và cho phép các công cụ khác tác động vào thông tin đó.

Higher-order functions (các hàm nhận tham số là các hàm khác) khá phổ biến trong Python. Mặc dù những hàm xử lý chuỗi như `map`, `filter`, hay `reduce` không được sử dụng nhiều, do list comprehensions và các cơ chế generator expressions được ưa chuộng hơn, các higher-order functions khác như `sorted`, `min`, `max` hay `functools.partial` lại thường xuyên được sử dụng.

Callables (các đối tượng "gọi được") có thể sinh ra bằng nhiều cách, từ lambda expression đơn giản, cho tới các đối tượng của các lớp có implement phương thức `__call__`. Mọi callables đều có thể được phát hiện thông qua hàm built-in `callable()` và hỗ trợ các cú pháp định nghĩa tham số đa dạng, bao gồm cả keyword-only parameters và annotations - hai tính năng mới được giới thiệu từ Python3.

Các hàm Python và các annotations (chú thích) của nó đều có những thuộc tính đa dạng có thể đọc bởi module `inspect`, thông qua phương thức như `Signature.bind` giúp định nghĩa các luật để gán giá trị một biến thực tế vào tham số định nghĩa trước.

Cuối cùng, chúng ta sẽ làm quen với các hàm nằm trong module `operator` cũng như `functools.partial` - các giải pháp hiệu quả thay thế cho cú pháp lambda vốn khó sử dụng.

---
### Table of Contents

- [Chapter 5: First Class Functions](#chapter-5-first-class-functions)
  - [Table of Contents](#table-of-contents)
  - [Functions as First Class Objects](#functions-as-first-class-objects)
  - [Functions That Apply on Iterable](#functions-that-apply-on-iterable)
  - [Annonymous Functions](#annonymous-functions)
  - [Making a callable object](#making-a-callable-object)
  - [Function introspection](#function-introspection)
  - [From Positional to Keyword Only Parameters](#from-positional-to-keyword-only-parameters)
  - [Retrieving Information about Parameters](#retrieving-information-about-parameters)
  - [Function Annotations](#function-annotations)
  - [Packages for Functional Programming](#packages-for-functional-programming)
    - [`operator`](#operator)
    - [`functools`](#functools)

---
### Functions as First Class Objects

Functions trong Python là các **first-class objects**, tức là nó có thể được:
-   Khởi tạo tại runtime
    ```python
    >>> def factorial(n):
    '''returns n!'''
    return 1 if n < 2 else n * factorial(n-1)

    >>> factorial(42)
    1405006117752879898543142606244511569936384000000000
    ```
-   Gán cho một biến hoặc một thành phần trong một cấu trúc dữ liệu nào đó
    ```python
    >>> fact = factorial
    >>> fact(5)
    120
    ```
-   Truyền vào hàm như là một tham số
    ```python
    >>> map(fact, range(11))
    [1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880, 3628800]
    ```
-   Trả về bởi một hàm khác (VD: decorators)
    
***Tricks:***
-   `__doc__`: xem hướng dẫn sử dụng (docstring) của một đối tượng bất kỳ (thông tin nằm trong cụm """...""" ngay sau khai báo function hoặc class)

---
### Functions That Apply on Iterable

Các hàm built-in phổ biến có khả năng thực thi trên iterable của Python là:
-   `sum`: Trả về tổng của chuỗi
-   `max`: Trả về phần tử lớn nhất chuỗi
-   `min`: Trả về phần tử nhỏ nhất chuỗi
-   `all`: Return `True` if all elements is truthy, `all([])` returns `True`
-   `any`: Return `True` if any element of iterable is truthy, `any([])` returns `False`
-   `map(func, iter)`: Trả về danh sách kết quả của việc thực hiện `func` trên từng phần tử của `iter`
    ```python
    >>> list(map(lambda x: x**2, range(1, 6)))
    [1, 4, 9, 16, 25]
    ```
-   `filter(func, iter)`: Trả về danh sách các phần tử của `iter` mà khi gọi qua `func` nhận được giá trị đúng (truthy values)
    ```python
    >>> list(filter(lambda x: x >= 0, range(-5, 5)))
    [0, 1, 2, 3, 4]
    ```
-   `reduce(func, iter)`: Với `func` là ánh xạ 2-1, `reduce` trả về một giá trị duy nhất từ `iter` bằng cách thực hiện `func` trên hai giá trị đầu tiên của iter, sau đó tiếp tục thực hiện `func` trên kết quả vừa nhận được và giá trị tiếp theo của `iter`,... tiếp tục cho đến hết `iter`:
    ```python
    >>> from functools import reduce
    >>> reduce((lambda x, y: x*y), range(1, 5)))
    24
    ```
---
### Annonymous Functions

Annonymous functions (hàm vô danh) là các hàm:
-   Không có tên và chỉ có thể sử dụng tại vị trí khai báo
-   Được khai báo bằng từ khóa `lambda`
-   Chỉ bao gồm một expression, không thể gán dữ liệu cho biến hay sử dụng các statement như `while, try, ...`

Bên ngoài phạm vi của higher-order functions, `lambda` không được sử dụng nhiều. Ví dụ một annonymous function:

```python
>>> fruits = ['strawberry', 'fig', 'apple', 'cherry', 'raspberry', 'banana']
>>> sorted(fruits, key=lambda word: word[::-1])
['banana', 'apple', 'fig', 'raspberry', 'strawberry', 'cherry']
```

---
### Making a callable object

Bất kỳ Python object nào cũng có thể là một callable nếu được implement phương thức `__call__`.

Do Python không có từ khóa `new` nên cú pháp dùng để khởi tạo một object và cú pháp gọi từ object đó là giống nhau: sử dụng cặp dấu ngoặc tròn `()`.

Ví dụ một callable:

```python
class BingoCage(object):
    def __init__(self, items):
        self._items = list(items)
        random.shuffle(self._items)
    def __call__(self):
        try:
            return self._items.pop()
        except IndexError:
            raise LookupError('pick from empty BingoCage')
    ...
>>> bingo = BingoCage(range(3))
>>> bingo()
2
```
---
### Function introspection

`dir()` vs `__dict__`: 
-   `__dict__` liệt kê ra các attribute mà object được implement
-   `dir()` liệt kê ra các attribute của object mà có thể được sử dụng (bao gồm cả các attribute được implement ở các lớp mà nó kế thừa ...)

Python functions có thể được gán thuộc tính (khiến nó gần như giống hệt một class instance). Bên cạnh đó nó còn chứa các built-in attribbutes riêng như: `__defaults__`, `__code__`, `__annotations__`, ...

---
### From Positional to Keyword Only Parameters

Một trong những tính năng tuyệt vời nhất của Python đó là cơ chế xử lý tham số đầu vào cực kỳ mềm dẻo.

Dưới đây là ví dụ về một hàm nhận vào bốn kiểu tham số và trả về một xâu HTML:

```python
def tag(name, *content, cls=None, **attrs):
    if cls is not None:
        attrs['class'] = cls
    if attrs:
        attr_str = ''.join (' {0}="{1}"'.format(attr, val)
                                    for attr, val in sorted(attrs.items()))
    else:
        attr_str = ''    
    
    if content:
        return '\n'.join('<{0}{1}>{2}</{0}>'.format(name, attr_str, c)
                                for c in content)
    else:
        return '<{0}{1}/>'.format(name, attr_str)
```

Các loại arguments trong Python bao gồm:
-   positional arguments:
    -   Các tham số ở vị trí cố định trong tương quan với các tham số khác
    -   Trong ví dụ trên, `name` là một positional arguments
    -   Các positional arguments phải được truyền vào hàm bởi người sử dụng và không được thay đổi vị trí
-   tuple argument:
    -   Mỗi tuple đại diện cho một số lượng tham số positional bất kỳ, cú pháp của tuple argument là: `*args`
    -   Trong ví dụ trên, `*content` là tham số kiểu tuple
    -   Mỗi hàm được phép có tối đa một tham số kiểu tuple 
-   keyword arguments:
    -   Các tham số khai báo bằng keyword, với cú pháp: `arg=default_value`
    -   Trong ví dụ trên, `cls` là một keyword argument
    -   Các keyword arguments nhận giá trị mặc định nếu không được chỉ định bởi người dùng
-   dict argument:
    -   Dict argument đại diện cho một số lượng bất kỳ keyword arguments, được khai báo với cú pháp `**kwargs`
    -   Trong ví dụ trên, `**attrs` là tham số kiểu dict
    -   Mỗi hàm có tối đa một tham số kiểu dict

Thứ tự các loại tham số trong chữ ký của hàm là:
```
positional -> tuple -> keyword -> dict
```

Khi gọi hàm, nếu tất cả tham số positional đã được truyền giá trị, các giá trị non-keyword còn lại được truyền vào biến tuple (nếu có), nếu không có biến tuple, các giá trị này được truyền vào các biến keyword (nếu có). Tương tự, nếu tất cả các tham số keyword được truyền giá trị, các giá trị keyword=value còn lại được truyền vào biến dict (nếu có).

Sử dụng hàm tag trong ví dụ ở trên:

```python
>>> tag('br')
'<br />'
>>>
>>> tag('p', 'hello')
'<p>hello</p>'
>>>
>>> print(tag('p', 'hello', 'world'))
<p>hello</p>
<p>world</p>
>>>
>>> tag('p', 'hello', id=33)
'<p id="33">hello</p>'
>>>
>>> print(tag('p', 'hello', 'world', cls='sidebar'))
<p class="sidebar">hello</p>
<p class="sidebar">world</p>
>>>
>>> tag(content='testing', name="img")
'<img content="testing" />'
>>>
>>> my_tag = {'name': 'img', 'title': 'Sunset Boulevard', 'src': 'sunset.jpg', 'cls': 'framed'}
>>> tag(**my_tag)
'<img class="framed" src="sunset.jpg" title="Sunset Boulevard" />'
```

**Tricks:**
-   `bool(sequence)` sẽ fallback về `sequence.__len__` nếu phương thức `__bool__` không được định nghĩa. Hiện tượng này xảy ra với cả list, tuple, set và dict

-   Gọi hàm theo cú pháp func(*args) với args là một tuple sẽ unpack tuple và truyền từng thành phần của nó vào hàm như các positional arguments. Tương tự, gọi hàm theo cú pháp func(**kwargs) với kwargs là một dict sẽ unpack dict và truyền từng thành phần của nó vào hàm như các keyword arguments

-   Định nghĩa một hàm có thể nhận bất kỳ loại và số lượng tham số nào như sau:
    ```python
    def func(*args, **kwargs):
        pass
    ```
-   python3 cho phép định nghĩa keyword-only arguments (tham số keyword chỉ nhận giá trị truyền vào có dạng keyword=value) bằng cú pháp như sau:
    ```python
    >>> def f(a, *, b):
    ...     return a, b
    ...
    >> f(1, 2)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: f() takes 1 positional argument but 2 were given

    >>> f(1, b=2)
    (1, 2)
    ```

---
### Retrieving Information about Parameters

Các thuộc tính chứa thông tin metadata của hàm là:
-   Thuộc tính `__defaults__` của một hàm lưu các giá trị mặc định cho positional và keyword arguments
-   Thuộc tính `__kwdefaults__` lưu các giá trị mặc định cho các keyword-only arguments
-   Thuộc tính `__code__` lưu tên của các tham số trong chữ ký hàm cùng với các biến cục bộ khai báo bởi hàm

Module `inspect` hỗ trợ việc lấy thông tin metadata từ hàm một cách dễ dàng hơn.

---
### Function Annotations

Function annotation là cơ chế xuất hiện từ Python 3, giúp lập trình viên thêm mô tả về kiểu dữ liệu của tham số cũng như giá trị trả về cho hàm của mình. Cú pháp chú thích  như sau:
-   Điều kiện cho tham số: `arg:data_type=default_value`
-   Điều kiện cho giá trị trả về: `func() -> return_type`

Ví dụ:
```python
def clip(text:str, max_len:'int > 0'=80) -> str:
    """Return text clipped at the last space before or after max_len
    """
    pass
```

Xem thông tin annotations của hàm bằng cách kiểm tra thuộc tính `__annotations__`:

```python
>>> clip.__annotations__
{'text': <class 'str'>, 'max_len': 'int > 0', 'return': <class 'str'>}
```

**Chú ý:** Annotations chỉ là metadata phục vụ hoạt động của IDE, frameworks hay decorators. Python không kiểm tra kiểu dữ liệu vào ra của một hàm có vi phạm annotations hay không.

**Đánh giá của người viết:** Function annotation là cơ chế giúp người dùng định nghĩa chính xác và rõ ràng cho API của mình. Song nó không ngăn chặn việc lập trình viên cố tình hay vô ý sử dụng sai kiểu dữ liệu. Nếu hàm bạn viết có mục đích là để cho người khác sử dụng, định nghĩa annotations là việc nên làm.

---
### Packages for Functional Programming

#### `operator`
  
Module `operator` chứa các hàm đại diện cho các toán tử trong Python, danh sách các hàm này có thể được xem tại [đây](https://docs.python.org/2/library/operator.html)

Việc sử dụng các hàm có ý nghĩa tương đương một toán tử chủ yếu nhằm mục đích truyền hàm đó vào một hàm khác. Dưới đây là các ví dụ:
-   Có thể dùng các hàm này thay cho cú pháp lambda trong `reduce`
    ```python
    >>> from operator import mul
    >>> from functools import reduce
    >>> reduce(mul, range(1,5))
    24
    ```
-   Sắp xếp các chuỗi bằng cách so sánh giá trị phần tử thứ `i` trong mỗi chuỗi sử dụng hàm `sorted` với toán tử `itemgetter(i)`:
    ```python
    >>> x = [1, 'a']; y = [2, 'z']; z = [3, 'g']
    >>> sorted([x, y, z], key=itemgetter(1))
    [[1, 'a'], [3, 'g'], [2, 'z']]
    ```
-   Tương tự, có thể dùng `attrgetter` để chỉ ra trường làm `key` cho hàm `sorted` để so sánh các đối tượng với nhau

#### `functools`
  
Module `functools` chứa các hàm tiện ích thường dùng với functions. Ví dụ:
-   `reduce`: Như đã lấy ví dụ ở trên
-   `partial`: Tạo ra hàm mới từ một hàm có sẵn với một vài tham số positional chỉ định trước:
    ```python
    >>> triple = partial(mul, 3)
    >>> triple(7)
    21
    ```
