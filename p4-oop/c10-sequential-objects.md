## Chapter 10: Sequence Hacking, Hashing and Slicing

Trong chương này, chúng ta sẽ tìm hiểu về những tính năng sau của Python thông qua ví dụ class `Vector` nhiều chiều:

-   Basic sequence protocol: `__len__` and `__getitem__` .
-   Safe representation of instances with many items.
-   Proper slicing support, producing new `Vector` instances.
-   Aggregate hashing taking into account every contained element value.
-   Custom formatting language extension.
-   Dynamic attribute access with `__getattr__`

---
### Table of Contents

- [Chapter 10: Sequence Hacking, Hashing and Slicing](#chapter-10-sequence-hacking-hashing-and-slicing)
  - [Table of Contents](#table-of-contents)
  - [Make Vector Compatible with Vector2d](#make-vector-compatible-with-vector2d)
  - [Protocol and Duck Typing](#protocol-and-duck-typing)
  - [A Slicable Vector](#a-slicable-vector)
  - [Vector with Dynamic Attribute Access](#vector-with-dynamic-attribute-access)
  - [Make Vector Hashable and Faster in Comparision](#make-vector-hashable-and-faster-in-comparision)
  - [Fancy Formatted Vector](#fancy-formatted-vector)
  - [Summary](#summary)
  - [Soapbox](#soapbox)

---
### Make Vector Compatible with Vector2d

Đầu tiên, hãy thử tạo ra một `Vector` với số chiều bất kỳ và tương thích với `Vector2d` - nghĩa là nó có thể làm tất cả những gì Vector2d có thể làm, với cú pháp tương tự. Đoạn code của chúng ta như sau:

```python
from array import array
import reprlib
import math

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
        return (type(self) == type(other) and
                tuple(self) == tuple(other))

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
-   Sử dụng `reprlib.repr()` để tạo ra một xâu đại diện ngắn gọn cho một `Vector` nhiều chiều (các chiều về sau được rút gọn thành dấu `...`). Bởi lẽ `rpr()` giúp phục vụ mục đích debugging, một `Vector` chiếm quá nhiều dòng trong file log sẽ gây rối mắt

---
### Protocol and Duck Typing

Trong ngữ cảnh của lập trình hướng đối tượng, *protocol* là một interface không chính thức, chỉ được định nghĩa trong documentation chứ không nằm trong code. Ví dụ, ở Chương 1, ta không cần phải thừa kế một class nào đặc biệt để tạo ra một sequence, chỉ cần implement `__len__` và `__getitem__` là đủ. Việc implement hai phương thức này chính là *protocol* để tạo ra một sequence. Một class tuân thủ sequence protocol có thể được sử dụng ở bất nơi nào mà đầu vào mong đợi là một sequence.

Ta nói một class *là* một sequence bởi vì nó *hành xử* như một sequence. Đây chính là khái niệm duck-typing:

> "If an animal quacks like a duck, walks like a duck, etc, then it is a duck."

Ta cũng có thể chỉ implement một phần của protocol, ví dụ như nếu chỉ muốn duyệt qua các phần tử của đối tượng thì class chỉ cần implement `__getitem__` là đủ.

---
### A Slicable Vector

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
>>> x = Vector(range(10))
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
...         return index
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
-   Nếu chỉ truy cập đến một phần tử, phương thức `__getitem__` sử dụng chính `index` kiểu `int`
-   Nếu ta dùng cú pháp slicing với cú pháp `s[<start>:<stop>:<step>]` thì tham số `index` của `__getitem__` là đối tượng `slice(<start>, <stop>, <step>)`
-   Nếu index là một `tuple` (trong cú pháp `s[1:4:2, 7:9]`), nó cũng sẽ chuyển thành `tuple` của các `slice` tương ứng. Tuy nhiên, sequence trong Python nhìn chung không hỗ trợ slicing với đầu vào là `tuple`, nên thường sẽ sinh ra một ngoại lệ `TypeError`

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

*Mô tả mã nguồn:*
-   Nếu index thuộc kiểu `slice`, ta tiến hành slice `_components` sử dụng `index` cho ra một `array` và dùng `array` này để tạo ra một đối tượng `Vector` mới. Như vậy, khi slice một `Vector` ta sẽ nhận về một `Vector` như mong muốn
-   Nếu index là kiểu số nguyên (`numbers.Integral`), trả về phần tử ở vị trí tương ứng trong `_components`
-   Nếu index thuộc kiểu khác, báo đầu vào không hợp lệ giống như các built-in sequences

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

---
### Vector with Dynamic Attribute Access

Khi implement một `Vector` nhiều chiều, ta đã làm mất đi tính chất truy cập thuộc tính theo tên của `Vector2d`, ta không thể dùng `v.x`, `v.y`, ... mà phải dùng chỉ số `v[0]`, `v[1]`, ...

Để giải quyết vấn đề này, ta có thể implement `__getattr__` để truy cập theo tên bốn phần tử đầu tiên của vector theo các thuộc tính `x`, `y`, `z`, `t` mà không cần định nghĩa trước như sau:

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

Giờ ta có thể lấy về giá trị của bốn phần tử đầu tiên dựa vào chữ cái tương ứng:

```python
>>> v = Vector(range(10))
>>> (v.x, v.y, v.z, v.t)
(0.0, 1.0, 2.0, 3.0)
```

Nhưng, tại đây nảy sinh một sự thiếu nhất quán trong hành vi của lớp `Vector`:

```python
>>> v = Vector(range(5))
>>> v.x
0.0
>>> v.x = 10
>>> v.x
10
>>> v
Vector([0.0, 1.0, 2.0, 3.0, 4.0])
```

Có thể thấy, việc gán `v.x` không làm thay đổi giá trị phần tử đầu tiên của vector `v`. Lý do là vì Python tra cứu thuộc tính `x` của đối tượng `v` theo thứ tự:
1.  Tìm kiếm trong `v` có lưu thuộc tính `x` không
2.  Tìm kiếm `x` trong `v.__class__`
3.  Tìm kiếm `x` tại nút tiếp theo trong đồ thị thừa kế (liên quan đến tính chất đa kế thừa, được đề cập đến ở Part 6)
4.  Cuối cùng, phương thức `__getattr__` mới được gọi để phân giải thuộc tính `x`. Do thuộc tính `x` đã được gán cho đối tượng `v`, quá trình tìm kiếm thuộc tính này đã dừng ngay ở bước đầu tiên mà không hề gọi đến phương thức `__getattr__`

Để giải quyết sự thiếu nhất quán này, cũng như đảm bảo các thuộc tính `x`, `y`, `z`, `t` không được cập nhật nhằm thỏa mãn tính chất immutable của `Vector`, ta cần implement hàm `__setattr__` để định nghĩa hành vi gán giá trị thuộc tính cho đối tượng `Vector` như sau:

```python
    ...
    def __setattr__(self, name, value):
        cls = type(self)
        if len(name) == 1 and name in cls.shortcut_names:
            msg = 'readonly attribute {!r}'
            raise AttributeError(msg.format(name))
        super().__setattr__(name, value)
```

Lúc này, gán các thuộc tính `x`, `y`, `z`, `t` cho `v` sẽ báo lỗi `AttributeError`:
```python
>>> v = Vector(range(5))
>>> v.x = 1
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/tmp/test.py", line 65, in __setattr__
    raise AttributeError(msg.format(name))
AttributeError: readonly attribute 'x'
>>>
>>> v.foo = "bar" # We can still set other attributes for v
```

*Chú ý:*
-   Thông thường, khi `__setattr__` chưa được định nghĩa, việc gán thuộc tính cho đối tượng được thực hiện bằng cách thêm thuộc tính vào `__dict__` 
    ```python
    obj.__dict__[name] = value
    ```
-   Khi `__setattr__` được implement, phương thức này được gọi thay vì gán vào `__dict__` như trên
-   Trong `__setattr__`, không nên dùng biểu thức `self.name=value` để tránh vòng lặp vô hạn. Thay vào đó, hãy dùng cú pháp sau:
    ```python
    super().__setattr__(name, value)
    ```

*Hãy luôn implement `__setattr__` bất kỳ khi nào bạn có ý định dùng `__getattr__` để đảm bảo tính nhất quán.*

---
### Make Vector Hashable and Faster in Comparision

Như ta đã biết, chỉ cần implement `__eq__` và `__hash__`, ta có thể biến Vector thành hasable:

```python
    
    def __eq__(self, other):
        return (type(self) == type(other) and
                tuple(self) == tuple(other))

    def __hash__(self):
        hashes = (hash(x) for x in self._components)
        return functools.reduce(operator.xor, hashes, 0)
```

*Mẹo:*
-   Tham số thứ ba trong hàm `reduce` là `initial_value`, nó là giá trị trả về nếu như sequence là rỗng, đồng thời cũng là giá trị đầu tiên được truyền vào vòng lặp tính toán của `reduce`. Thói quen tốt là gán giá trị này bằng `0` cho các phép `+`, `|`, `^`, và bằng `1` cho các phép `*`, `&`.

Code phương thức `__eq__` ở trên rõ ràng là chưa tối ưu, ta phải tạo ra hai tuple mới để so sánh hai Vector, điều mà có thể gây tốn kém chi phí nếu hai vector có số chiều lớn. Để implement phương thức này nhanh và tiết kiệm hơn, hãy duyệt qua hai Vector và so sánh từng phần tử với nhau:

```python
    def __eq__(self, other):
        return (len(self) == len(other) and
                all(a == b for a, b in zip(self, other)))
```

*Mẹo*:
-   Hàm `all` có thể nhận tham số là một generator expression, giúp phép so sánh các phần tử thuộc hai chuỗi trông ngắn gọn và bắt mắt hơn (bên cạnh việc tăng tốc so sánh nhờ các cơ chế tính toán song song của OS)
-   `zip` là hàm tiện ích hỗ trợ lặp đồng thời qua các sequences. Nó tạo ra một generator, trong mỗi bước lặp, generator này yield một tuple chứa các phần tử có cùng index của các sequence được truyền vào. Chú ý rằng `zip` sẽ dừng sau khi duyệt xong chuỗi ngắn nhất

---
### Fancy Formatted Vector

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

*Mẹo:*
-   `itertools.chain` là hàm giúp tạo một iterator duyệt qua lần lượt tất cả các chuỗi được truyền vào hàm

---
### Summary

-   Create customize sequences that can act like built-in sequences just by implementing `__getitem__` và `__len__`. These mechanisms are called protocol - the informal interfaces used in duck-typed language

-   Create Vectors that can be sliced properly by handling different types of argument in `__getitem__` method

-   Implement `__getattr__` to tell Python how to get attributes that are not pre-defined in the object

-   Implement `__setattr__` to apply restrictions when assigning attributes

-   Apply reduce functions on sequences (`all`, `sum`, `reduce(operator.xor)`, ...)

---
### Soapbox

> TBD