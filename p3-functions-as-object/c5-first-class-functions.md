# FluentPython-P3-C5: First Class Functions

The goal of this chapter was to explore the first-class nature of functions in Python. The main ideas are that you can assign functions to variables, pass them to other functions, store them in data structures and access function attributes, allowing frameworks and tools to act on that information. Higher-order functions, a staple of functional programming, are common in Python - even if the use of map , filter and reduce is not as frequent as it was - thanks to list comprehensions (and similar constructs like generator expressions) and the appearance of reducing built-ins like sum , all and any . The `sorted` , `min` , `max` built-ins, and `functools.partial` are examples of commonly used higher-order functions in the language.

Callables come in seven different flavors in Python, from the simple functions created with lambda to instances of classes implementing `__call__` . They can all be detected by the `callable()` built-in. Every callable supports the same rich syntax for declaring formal parameters, including keyword-only parameters and annotations - both new features introduced with Python 3.

Python functions and their annotations have a rich set of attributes that can be read
with the help of the inspect module, which includes the Signature.bind method to
apply the flexible rules that Python uses to bind actual arguments to declared parameters.

Lastly, we covered some functions from the operator module and `functools.partial` , which facilitate functional programming by minimizing the need for the
functionally-challenged lambda syntax.

## Table of Contents

*   [Functions as First Class Objects](#functions-as-first-class-objects)
*   [Functions That Apply on Iterable](#functions-that-is-applied-on-iterable)
*   [Annonymous Functions](#annonymous-functions)
*   [Making a callable object: ](#making-a-callable-object-)
*   [Function introspection:](#function-introspection)
*   [From Positional to Keyword Only Parameters](#from-positional-to-keyword-only-parameters)
*   [Retrieving Information about Parameters](#retrieving-information-about-parameters)
*   [Function Annotations](#function-annotations)
*   [Packages for Functional Programming](#packages-for-functional-programming)


## Functions as First Class Objects

*   Functions trong Python là các **first-class objects**, tức là nó có thể được:
    *   Khởi tạo tại runtime
    ```python
    >>> def factorial(n):
    '''returns n!'''
    return 1 if n < 2 else n * factorial(n-1)

    >>> factorial(42)
    1405006117752879898543142606244511569936384000000000
    ```
    *   Gán cho một biến hoặc một element trong một cấu trúc dữ liệu nào đó
    ```python
    >>> fact = factorial
    >>> fact(5)
    120
    ```
    *   Truyền vào hàm như là một tham số
    ```python
    >>> map(fact, range(11))
    [1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880, 3628800]
    ```
    *   Trả về bởi một hàm khác (VD: decorators)
    
***Tricks:***
*   `__doc__`: xem hướng dẫn sử dụng của một đối tượng bất kỳ (thông tin nằm trong cụm """...""" ngay sau khai báo function hoặc class)

## Functions That Apply on Iterable

*   `sum`: Trả về tổng của chuỗi
*   `max`: Trả về phần tử lớn nhất chuỗi
*   `min`: Trả về phần tử nhỏ nhất chuỗi
*   `all`: Return `True` if all elements is truthy, `all([])` returns `True`
*   `any`: Return True if any element of iterable is truthy, `any([])` returns `False`
*   `map(func, iter)`: `func` là ánh xạ 1-1, `map` trả về danh sách kết quả của việc thực hiện `func` trên từng phần tử của `iter`
    ```python
    >>> list(map(lambda x: x**2, range(1, 6)))
    [1, 4, 9, 16, 25]
    ```
*   `filter(func, iter)`: `func` là một hàm trả về giá trị boolean, `filter` trả về danh sách các phần tử của `iter` mà nhận giá trị `True` khi truyền vào `func`
    ```python
    >>> list(filter(lambda x: x >= 0, range(-5, 5)))
    [0, 1, 2, 3, 4]
    ```
*   `reduce(func, iter)`: `func` là ánh xạ 2-1, `reduce` trả về một giá trị duy nhất từ `iter` bằng cách thực hiện `func` trên hai giá trị đầu tiên của iter, sau đó tiếp tục thực hiện `func` trên kết quả vừa nhận được và giá trị tiếp theo của `iter`, ... Cứ thế tiếp tục cho đến khi duyệt hết chuỗi `iter` được kết quả là một giá trị duy nhất:
    ```python
    >>> reduce((lambda x, y: x*y), range(1, 5)))
    24
    ```
## Annonymous Functions

*   Hàm vô danh là hàm không có tên và do vậy không thể được sử dụng lại, chỉ có thể sử dụng nó tại vị trí khai báo
*   Được khai báo bằng từ khóa `lambda`
*   Mỗi annonymous function chỉ bao gồm một expression, không thể gán dữ liệu cho biến hay sử dụng các statement như `while, try, ...`
*   Bên ngoài context của high-order functions (hàm nhận tham số là một hàm khác), `lambda` không được sử dụng nhiều
*   Ví dụ:
    ```python
    >>> fruits = ['strawberry', 'fig', 'apple', 'cherry', 'raspberry', 'banana']
    >>> sorted(fruits, key=lambda word: word[::-1])
    ['banana', 'apple', 'fig', 'raspberry', 'strawberry', 'cherry']
    ```

## Making a callable object

*   Bất kỳ Python object nào cũng có thể là một callable nếu được implement phương thức `__call__`
*   Do Python không có từ khóa `new` nên cú pháp dùng để khởi tạo một object và cú pháp gọi từ object đó là giống nhau
*   Ví dụ:

    ```python
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
## Function introspection

*   `dir()` vs `__dict__`: 
    *   `__dict__` liệt kê ra các attribute mà object được implement
    *   `dir()` liệt kê ra các attribute của object mà có thể được sử dụng (bao gồm cả các attribute được implement ở các lớp mà nó kế thừa ...)

*   Function attributes: Python functions có thể chứa các thuộc tính (khiến nó gần như giống hệt một class instance), tuy nhiên nó có chứa các built-in attribbutes riêng như: `__defaults__`, `__code__`, `__annotations__`, ...

## From Positional to Keyword Only Parameters

*   Một trong những tính năng tuyệt vời nhất của Python đó là cơ chế xử lý tham số đầu vào cực kỳ mềm dẻo. Dưới đây là ví dụ về một hàm có thể sinh ra một thẻ HTML bất kỳ với Python:

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

*   Các loại arguments trong Python bao gồm:

    *   positional arguments:
        *   Các tham số ở vị trí cố định trong tương quan với các loại tham số khác
        *   Trong ví dụ trên, `name` là một positional arguments
        *   Các positional arguments phải được truyền vào hàm bởi người sử dụng và phải luôn ở vị trí bắt buộc của nó
    *   tuple argument:
        *   Mỗi tuple đại diện cho một số lượng tham số bất kỳ, cú pháp của tuple argument là: `*args`
        *   Trong ví dụ trên, `*content` là tham số kiểu tuple
        *   Mỗi hàm được phép có tối đa một tham số kiểu tuple 
    *   keyword arguments:
        *   Các tham số khai báo bằng keyword, với cú pháp: `arg=default_value`
        *   Trong ví dụ trên, `cls` là một keyword argument
        *   Các keyword arguments nhận giá trị mặc định nếu không được truyền vào hàm
    *   dict argument:
        *   Dict argument đại diện cho một số lượng bất kỳ keyword arguments, được khai báo với cú pháp `**kwargs`
        *   Trong ví dụ trên, `**attrs` là tham số kiểu dict
        *   Mỗi hàm có tối đa một tham số kiểu dict

*   Thứ tự các loại tham số trong chữ ký của hàm là:

        positional -> tuple -> keyword -> dict

*   Khi gọi hàm, nếu tất cả tham số positional đã được truyền giá trị, các giá trị non-keyword còn lại được truyền vào biến tuple (nếu có), nếu không có biến tuple, các giá trị này được truyền vào các biến keyword (nếu có). Tương tự, nếu tất cả các tham số keyword được truyền giá trị, các giá trị keyword=value còn lại được truyền vào biến dict (nếu có).

Sử dụng hàm tag trong ví dụ ở trên:

```python
>>> tag('br')
'<br />'
>>> tag('p', 'hello')
'<p>hello</p>'
>>> print(tag('p', 'hello', 'world'))
<p>hello</p>
<p>world</p>
>>> tag('p', 'hello', id=33)
'<p id="33">hello</p>'
>>> print(tag('p', 'hello', 'world', cls='sidebar'))
<p class="sidebar">hello</p>
<p class="sidebar">world</p>
>>> tag(content='testing', name="img")
'<img content="testing" />'
>>> my_tag = {'name': 'img', 'title': 'Sunset Boulevard', 'src': 'sunset.jpg', 'cls': 'framed'}
>>> tag(**my_tag)
'<img class="framed" src="sunset.jpg" title="Sunset Boulevard" />'
```

**Tricks:**
*   `bool(sequence)` sẽ fallback về `sequence.__len__` nếu phương thức `__bool__` không được định nghĩa. Hiện tượng này xảy ra với cả list, tuple, set và dict

*   Gọi hàm theo cú pháp func(*args) với args là một tuple sẽ unpack tuple và truyền từng thành phần của nó vào hàm như các positional arguments. Tương tự, gọi hàm theo cú pháp func(**kwargs) với kwargs là một dict sẽ unpack dict và truyền từng thành phần của nó vào hàm như các keyword arguments

*   Định nghĩa một hàm có thể nhận bất kỳ loại và số lượng tham số nào như sau:
    ```python
    def func(*args, **kwargs):
        pass
    ```
*   python3 cho phép định nghĩa keyword-only arguments (tham số keyword chỉ nhận giá trị truyền vào có dạng keyword=value) bằng cú pháp như sau:
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

## Retrieving Information about Parameters

*   Thuộc tính `__defaults__` của một hàm lưu các giá trị mặc định cho positional và keyword arguments
*   Thuộc tính `__kwdefaults__` lưu các giá trị mặc định cho các keyword-only arguments
*   Thuộc tính `__code__` lưu tên của các tham số trong chữ ký hàm cùng với các biến cục bộ khai báo bởi hàm
*   Module `inspect`hỗ trợ việc lấy thông tin metadata từ hàm một cách dễ dàng hơn

## Function Annotations

*   Python 3 cung cấp cơ chế giúp chỉ định kiểu tham số và kiểu trả về cho hàm
*   Đặt điều kiện cho tham số: `arg:data_type=default_value`
*   Điều kiện cho giá trị trả về: `func() -> return_type`
*   Một ví dụ về Python annotaion:

    ```python
    def clip(text:str, max_len:'int > 0'=80) -> str:
        """Return text clipped at the last space before or after max_len
        """
        pass
    ```
*   Xem thông tin annotations của hàm:
    ```python
    >>> clip.__annotations__
    {'text': <class 'str'>, 'max_len': 'int > 0', 'return': <class 'str'>}
    ```
*   Các giá trị này chỉ được lưu trong `__annotation__` attribute như là metadata phục vụ hoạt động của IDE, frameworks hay decorators. Không có thao tác kiểm tra hay xác thực nào được thực hiện đối với các thông tin này

## Packages for Functional Programming

*   Module **operator**:
    *   Chứa các hàm đại diện cho các toán hạng trong Python, danh sách các hàm này có thể được xem tại [đây](https://docs.python.org/2/library/operator.html)
    *   Việc sử dụng các hàm có ý nghĩa tương đương một toán hạng chủ yếu nhằm mục đích truyền hàm đó vào một hàm khác
    *   Có thể dùng các hàm này thay cho cú pháp lambda trong `reduce`:
        ```python
        >>> reduce(mul, range(1,5))
        24
        ```
    *   Sử dụng `itemgetter(i)` để lấy ra vị trí `i` của một sequence bất kỳ, tương tự như cú pháp `sequence[i]`. Có thể sử dụng hàm này như `key` trong cú pháp `sorted` để chỉ ra vị trí dùng để so sánh hay sequences với nhau:
        ```python
        >>> x = [1, 'a', 'asd']; y = [2, 'z', 'gsd']; z = [3, 'g', 'mnp']
        >>> sorted([x, y, z], key=itemgetter(1))
        [[1, 'a', 'asd'], [3, 'g', 'mnp'], [2, 'z', 'gsd']]
        ```
    *   Tương tự, có thể dùng `attrgetter` để chỉ ra trường làm `key` cho hàm `sorted` để so sánh các đối tượng với nhau

*   Module **functools**:
    *   Chứa các hàm tiện ích khá hữu dụng, thường gặp nhất là `reduce` (đã đề cập đến ở trên, lưu ý rằng từ python3 trở đi reduce không còn là built in nữa nên phải khai báo nó trước khi dùng)
    *   Một hàm tiện ích khác hay được dùng là `partial`, nó có chức năng tạo ra hàm mới từ một hàm có sẵn với một hoặc một vài tham số positional được gắn cố định:
        ```python
        >>> triple = partial(mul, 3)
        >>> triple(7)
        21
        ```
