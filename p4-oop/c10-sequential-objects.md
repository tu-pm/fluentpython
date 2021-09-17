# Sequence Hacking, Hashing and Slicing

Trong chương này, chúng ta sẽ tìm hiểu về những tính năng sau của Python thông qua ví dụ class `Vector` nhiều chiều:

-   Basic sequence protocol: `__len__` and `__getitem__` .
-   Safe representation of instances with many items.
-   Proper slicing support, producing new `Vector` instances.
-   Aggregate hashing taking into account every contained element value.
-   Custom formatting language extension.
-   Dynamic attribute access with `__getattr__`

## Make Vector Compatible with Vector2d

Đầu tiên, hãy thử tạo ra một `Vector` tương thích với Vector2d, nghĩa là nó có thể làm tất cả những gì Vector2d có thể làm, với cú pháp tương tự. Đoạn code của chúng ta như sau:

```python
class Vector(object):

    typecode = 'd'

    def __init__(self, components):
        self._components = array(self.typecode, components)

    def __iter__(self):
        return iter(self._components)

    def __repr__(self):
        components = reprlib.repr(self._components)
        components = components[components.find('['):-1]
        return 'Vector({})'.format(components)

    def __str__(self):
        return str(tuple(self))

    def __bytes__(self):
        return (bytes([ord(self.typecode)]) +
                bytes(self._components))

    def __eq__(self, other):
        return type(self) == type(other) and
               tuple(self) == tuple(other)

    def __abs__(self):
        return math.sqrt(sum(x*x for x in self))

    def __bool__(self):
        return bool(abs(self))

    @classmethod
    def frombytes(cls, octets):
        typecode = chr(octets[0])
        memv = memoryview(octets[1:]).cast(typecode)
        return cls(memv)
```
Một vài chú ý:

-   `__init__` constructor của class `Vector` không tương thích với Vector2d. Ta có thể khiến chúng tương thích nhau bằng cách sử dụng cú pháp `*args`. Tuy nhiên, các tốt nhất để viết constructor cho một kiểu sequence đó là lấy tham số kiểu iterable, giống như cách mà các built-in sequences làm
-   Sử dụng `reprlib.repr()` để tạo ra một xâu đại diện ngắn gọn cho một `Vector` nhiều chiều (các chiều về sau được rút gọn thành dấu `...`). Bởi lẽ `rpr()` giúp phục vụ mục đích debugging, một `Vector` chiếm quá nhiều dòng trong file log sẽ không giúp được gì ngoài việc gây thêm rắc rối

## Protocol and Duck Typing

Trong ngữ cảnh của lập trình hướng đối tượng, *protocol* là một interface không chính thức, chỉ được định nghĩa trong documentation chứ không nằm trong code. Ví dụ, ở Chương 1, ta không cần phải thừa kế một class nào đặc biệt để tạo ra một sequence, chỉ cần implement `__len__` và `__getitem__` là đủ. Việc implement hai phương thức này chính là *protocol* để tạo ra một sequence. Một class tuân thủ sequence protocol có thể được sử dụng ở bất nơi nào mà đầu vào mong đợi là một sequence.

Ta nói một class *là* một sequence bởi vì nó *hành xử* như một sequence. Đây chính là khái niệm duck-typing:

        "If an animal quacks like a duck, walks like a duck, etc, then it is a duck."

Ta cũng có thể chỉ implement một phần của protocol, ví dụ như nếu muốn class chỉ hỗ trợ iteration thì chỉ cần implement `__getitem__` là đủ.

## A Slicable Vector

Chỉ cần biến `Vector` thành sequence là nó đã trở thành slicable:

```python
...
    def __len__(self):
        return len(self._components)
    def __getitem__(self, index):
        return self._components[index]
```

Thử slice một đối tượng Vector:

```python
>>> x = Vector(xrange(10))
>>> x[0], x[-1]
(0.0, 9.0)
>>> x[1:4]
array('d', [1.0, 2.0, 3.0])
```
Vẫn chưa tốt lắm, ta cần kết quả trả về khi slice một `Vector` là một `Vector`, chứ không phải là một `array`. Để làm được điều này, ta cần phải implement `__getitem__` theo cách khác. Nhưng trước hết hãy thử tìm hiểu xem cơ chế slicing của Python là thế nào.

Quan sát ví dụ sau:

```python
>>> class MySeq:
    ...     def __getitem__(self, index):
    ...     return index
    ...
>>> s = MySeq()
>>> s[1]
1
>>> s[1:4]
slice(1, 4, None)
>>> s[1:4:2]
slice(1, 4, 2)
>>> s[1:4:2, 9]
(slice(1, 4, 2), 9)
>>> s[1:4:2, 7:9]
(slice(1, 4, 2), slice(7, 9, None))
```
*Nhận xét:*

-   Ta implement phương thức `__getitem__` sao cho nó trả về chính tham số mà nó nhận vào, mục đích là để xem python sử dụng phương thức này như thế nào khi slice một sequence
-   Nếu chỉ truy cập đến một phần tử, hay index là kiểu `int`, phương thức `__getitem__` sử dụng chính index đó
-   Nếu ta dùng cú pháp slicing, index được sử dụng với cú pháp `start:stop:step` thì nó sẽ được chuyển thành một đối tượng `slice(start:stop:step)` khi truyền index vào hàm `__getitem__`
-   Nếu index là một tuple (trong cú pháp `s[1:4:2, 7:9]`), nó cũng sẽ chuyển thành tuple của các slice tương ứng. Tuy nhiên, sequence trong Python nhìn chung không hỗ trợ slicing với đầu vào là tuple, bởi vậy, nếu index là tuple thì nên có một ngoại lệ `TypeError` được báo

Từ ví dụ trên, ta biết rằng, hai đầu vào hợp lệ của hàm `__getitem__` khi nó được gọi bởi trình thông dịch đó là kiểu `int` và kiểu `slice`. Bây giờ ta sẽ implement phương thức này sao cho nó xử lý được với các đầu vào khác nhau như sau:

```python
    import numbers
    ...
    def __getitem__(self, index):
        cls = type(self)
        if isinstance(index, slice):
            return cls(self._components[index])
        elif isinstance(index, numbers.Integral):
            return self._components[index]
        else:
            msg = '{cls.__name__} indices must be integers'
            raise TypeError(msg.format(cls=cls))
```

*Chú ý:*

-   Nếu index thuộc kiểu `slice`, slice `_components` theo index được một `array` và dùng `array` này để tạo ra một đối tượng `Vector` mới. Như vậy, khi slice một `Vector` ta sẽ nhận về một `Vector`, đúng như mong muốn

-   Nếu index là kiểu `int` hoặc kiểu số nguyên khác, trả về phần tử ở vị trí tương ứng trong `_components`

-   Với các đầu vào khác, báo lỗi đầu vào không hợp lệ (bắt chước theo các built-in sequences). Chú ý cú pháp format string đã được nói đến trong chương 9

Bây giờ, ta có thể slice `Vector` giống như slice các kiểu built-in khác:

```python
>>> x = Vector(range(10))
>>> x[5]
5.0
>>> x[1::2]
Vector([1.0, 3.0, 5.0, 7.0, 9.0])
>>> x[1, 3]
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "c10.py", line 55, in __getitem__
    raise TypeError(msg.format(cls=cls))
TypeError: Vector indices must be integers
```

Đến đây, bạn, cũng như tôi, có thể đặt câu hỏi là tại sao phải tốn công implement những phương thức này làm gì khi chỉ cần thừa kế built-in classes là xong. Ví dụ như muốn `Vector` hành xử như `list` thì cho nó kế thừa `list` là xong? Câu trả lời sẽ được đề cập đến ở chương 12, hãy tiếp tục đọc đến đó.

## Vector with Dynamic Attribute Access

Khi implement một `Vector` nhiều chiều, ta đã làm mất đi tính chất truy cập thuộc tính theo tên của `Vector2d`, ta không thể dùng `v.x`, `v.y`, ... mà phải dùng chỉ số `v[0]`, `v[1]`, ...

Tất nhiên ta có cách để khắc phục vấn đề này, dù việc đó không thực sự cần thiết. Dưới đây ta sẽ bàn đến hai magic methods khác, đó là `__getattr__` và `__setattr__`.

Đầu tiên là `__getattr__`, nó được sử dụng nhằm mục đích:
-   Định nghĩa cách tra cứu một thuộc tính không nằm trong đối tượng
-   Có vai trò như *getter* chống truy cập trái phép tới thuộc tính này

Python tra cứu thuộc tính `x` của đối tượng `obj` như sau:

1.  Tìm kiếm trong `obj` có lưu thuộc tính `x` không
2.  Tìm kiếm `x` trong `obj.__class__`
3.  Tìm kiếm `x` tại nút tiếp theo trong đồ thị thừa kế (đây là khái niệm rất hay ho và khá phức tạp bởi Python hỗ trợ đa kế thừa, nội dung này được đề cập tới ở Part VI)
4.  Sử dụng phương thức `__getattr__` là phương thức fall back cho thao tác tìm kiếm

Ta có thể implement `__getattr__` để truy cập theo tên bốn phần tử đầu tiên của vector như sau:

```python
    shortcut_names = 'xyzt'
    def __getattr__(self, name):
        cls = type(self)
        if len(name) == 1:
            pos = cls.shortcut_names.find(name)
            if 0 <= pos < len(self._components):
                return self._components[pos]
        msg = '{.__name__} object has no attribute {!r}'
        raise AttributeError(msg.format(cls, name))
```

Tuy nhiên, việc implement chỉ phương thức `__getattr__` là không đủ. Giả sử ta muốn gán `obj.x = 3` chẳng hạn, khi đó `obj` sẽ được tạo một attribute mới là `x = 3`, thay vì thay đổi giá trị của phần tử đầu tiên thành 3. Hơn nữa, các attribute `xyzt` nên là read-only, giống như `Vector2d`.

Sử dụng `__setattr__` để chỉ định cách thức gán giá trị nào đó cho biến nào đó:

```python
    ...
    def __setattr__(self, name, value):
        cls = type(self)
        if len(name) == 1 and name in cls.shortcut_names:
            msg = 'readonly attribute {!r}'
            raise AttributeError(msg.format(name))
        super().__setattr__(name, value)
```

*Chú ý:*

-   Khi `__setattr__` được implement, phương thức này được gọi thay cho cách gán thông thường (thêm `name:value` trực tiếp vào `__dict__`)
-   Trong `__setattr__`, tốt nhất không nên tồn tại cú pháp `self.name=value`, nó sẽ khiến phương thức này bị gọi lại lần nữa và chương trình bị rơi vào vòng lặp vô hạn. Hai cách nên được dùng khi gán attribute trong `__setattr__` là:
    1.  Gán trực tiếp vào `dict`:
        ```python
        self.__dict__[name] = value
        ```
    2.  Gọi đến phương thức `__setattr__` của base class:
        ```python
        super().__setattr__(name, value)
        ```
-   Cách gán thứ 2 được khuyên dùng, bởi vì nếu base class cũng implement phương thức `__setattr__`, quá trình kiểm tra điều kiện khi gán được thực hiện tiếp ở lớp này, sau đó mới gán giá trị (hoặc có thể chuyển đến nút tiếp theo, cho tới tận nút gốc là `object`).

## Make Vector Hashable and Faster in Comparision

Như ta đã biết, chỉ cần implement `__eq__` và `__hash__`, ta có thể biến Vector thành hasable:

```python
    
    def __eq__(self, other):
        return type(self) == type(other) and \
               tuple(self) == tuple(other)

    def __hash__(self):
        hashes = (hash(x) for x in self._components)
        return functools.reduce(operator.xor, hashes, 0)
```

*Chú ý:* Tham số thứ ba trong hàm `reduce` là `initial_value`, nó là giá trị trả về nếu như sequence là rỗng, đồng thời cũng là giá trị đầu tiên được truyền vào vòng lặp tính toán của `reduce`. Thói quen tốt là gán giá trị này bằng 0 cho các phép +, |, ^, bằng 1 cho các phép *, &.

Code phương thức `__eq__` ở trên rõ ràng là chưa tối ưu, ta phải tạo ra hai tuple mới để so sánh hai Vector, điều mà có thể gây tốn kém chi phí nếu hai vector có số chiều lớn. Để implement phương thức này nhanh và tiết kiệm hơn, hãy duyệt qua hai Vector và so sánh từng phần tử với nhau:

```python
    def __eq__(self, other):
        return len(self) == len(other) and \
                   all(a == b for a, b in zip(self, other))
```

*Chú ý*:

-   Hàm `all` có thể nhận tham số là một generator expression, giúp phép so sánh các phần tử thuộc hai chuỗi trông ngắn gọn và bắt mắt hơn (bên cạnh việc tăng tốc so sánh nhờ các cơ chế tính toán song song được cài đặt)

-   `zip` là hàm tiện ích hỗ trợ lặp đồng thời qua các sequences. Nó tạo ra một generator, trong mỗi bước lặp, generator này yield một tuple chứa các phần tử có cùng index của các sequence được truyền vào. Chú ý rằng `zip` sẽ dừng sau khi duyệt xong chuỗi ngắn nhất

## Fancy Formatted Vector

Lớp `Vector2d` được implement phương thức `__format__` sao cho nó có khả năng biểu diễn vector dưới dạng tọa độ cực. Mở rộng với vector nhiều chiều, lớp `Vector` cũng cần được biểu diễn dưới dạng tọa độ siêu cầu (hyperspherical).

Cụ thể, ta sẽ dùng ký tự 'h' để định nghĩa format suffix cho cách biểu diễn tọa độ siêu cầu. Format của dạng tọa độ này là `<r, theta1, theta2, ..., thetaN>` với N+1 là số chiều của vector, `r` là độ dài vector, `thetai` là góc tọa độ thứ i.

```python
    def angle(self, n):
        r = math.sqrt(sum(x*x for x in self[n:]))
        a = math.atan2(r, self[n-1])
        if (n == len(self) -1) and (self[-1] < 0):
            return math.pi * 2 - a
        else:
            return a

    def angles(self):
        return (self.angle(n) for n in range(1, len(self)))

    def __format__(self, fmt_spec=''):
        if fmt_spec.endswith('h'):
            fmt_spec = fmt_spec[:-1]
            coords = itertools.chain([abs(self)], self.angles())
            outer_fmt = '<{}>'
        else:
            coords = self
            outer_fmt = '({})'

        components = (format(c, fmt_spec) for c in coords)
        return outer_fmt.format(', '.join(components))
```

*Chú ý:*

-   `itertools.chain` là hàm giúp tạo một iterator duyệt qua lần lượt tất cả các chuỗi được truyền vào hàm

## Chapter Summary

-   Create customize sequences that can act like built-in sequences just by implementing `__getitem__` và `__len__`. These mechanisms are called protocol - the informal interfaces used in duck-typed language

-   Create Vectors that can be sliced properly by handling different types of argument in `__getitem__` method

-   Implement `__getattr__` to tell Python how to get attributes that are not pre-defined in the object

-   Implement `__setattr__` to apply restrictions when assigning attributes

-   Apply reduce functions on sequences (`all`, `sum`, `reduce(operator.xor)`, ...)

