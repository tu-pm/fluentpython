## Chapter 9: A Pythonic Object

Python data model giúp đối tượng tạo ra bởi người dùng có thể hành xử như một đối tượng thuộc kiểu built-in. Chapter này sẽ đề cập đến một vài hành vi như thế và cách implement nó trong đối tượng của bạn, bao gồm:
-    Trả về xâu đại diện cho đối tượng qua các hàm như `str()`, `repr()` hay `bytes()`
-    Tạo ra nhiều constructor khác nhau bằng cách sử dụng class methods
-    Format đối tượng qua hàm `format()` và phương thức `str.format()`
-    Tạo ra các thuộc tính chỉ đọc cho đối tượng
-    Tạo ra các đối tượng *hashable* để truyền vào set hoặc dict keys
-    Sử dụng bộ nhớ một cách tiết kiệm bằng `__slots__`

---
### Table of Contents

- [Chapter 9: A Pythonic Object](#chapter-9-a-pythonic-object)
  - [Table of Contents](#table-of-contents)
  - [Object Representations](#object-representations)
  - [Vector Class Redux](#vector-class-redux)
  - [Class Methods vs Static Methods](#class-methods-vs-static-methods)
    - [Class Methods](#class-methods)
    - [Static Methods](#static-methods)
  - [Formatted Displays](#formatted-displays)
    - [Placeholder in String Format Method](#placeholder-in-string-format-method)
    - [Implement User Defined Format Specification](#implement-user-defined-format-specification)
  - [A Hashable Vector2d](#a-hashable-vector2d)
  - [Private and Protected Attributes in Python](#private-and-protected-attributes-in-python)
  - [Saving Space with the __slots__ Class Attribute](#saving-space-with-the-slots-class-attribute)
  - [Overriding Class Attributes](#overriding-class-attributes)
  - [Summary](#summary)
  - [Soapbox](#soapbox)

---
### Object Representations

Hai cách chủ yếu được sử dụng để lấy ra thông tin đại diện cho một object bất kỳ dưới dạng một xâu trong Python:
-   `repr()`: Trả về thông tin mà developers cần
-   `str()`: Trả về thông tin mà người dùng cần

Để sử dụng hai hàm này với một object, nó cần được implement hai phương thức tương ứng là `__repr__` và `__str__`. Do `str()` sẽ fallback về `__repr__` nếu `__str__` không được implement nên nếu phải lựa chọn, người lập trình nên định nghĩa phương thức `__repr__` là tối thiểu.

Ví dụ:
```python
>>> class Cat(object):
...     def __init__(self, name, kind):
...         self.name = name
...         self.kind = kind
...     
...     def __str__(self):
...         return "My name is %s" % self.name
...     
...     def __repr__(self):
...         return "My name is %s, I'm a %s cat" % (self.name, self.kind)
... 
>>> cat = Cat("Pun", "Persian")
>>> str(cat)
'My name is Pun'
>>> repr(cat)
"My name is Pun, I'm a Persian cat"
```

Hai cách tạo ra đối tượng đại diện khác cho objects là `bytes()` và `format()`, ví dụ về cách sử dụng chúng được đề cập ở những phần sau.

---
### Vector Class Redux

Dưới đây là một ví dụ về Pythonic Vector2d class, vector này có thể được:

-   In ra màn hình bằng hàm `print()`
-   Unpack thành một tuple chứa hoành độ và tung độ của vector
-   Tính độ dài với lệnh `abs()`
-   Trả về tính đúng với lệnh `bool()` (Vector là `False` nếu và chỉ nếu nó có độ dài bằng 0)
-   So sánh bằng nhau với vector khác bằng cú pháp `==`

```python
from array import array
import math

class Vector2d(object):
    typecode = 'd'

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def __iter__(self):
        return (i for i in (self.x, self.y))

    def __repr__(self):
        class_name = type(self).__name__
        return '{}({!r}, {!r})'.format(class_name, *self)

    def __str__(self):
        return str(tuple(self))

    def __eq__(self, other):
        return type(self) == type(other) and tuple(self) == tuple(other)

    def __abs__(self):
        return math.hypot(self.x, self.y)

    def __bool__(self):
        return bool(abs(self))

...
>>> x = Vector2d(1, 2)
>>> 
>>> print(x)
(1.0, 2.0)
>>> 
>>> lat, long = x   
>>> print(lat, long)
1.0 2.0
>>> 
>>> abs(x)
2.23606797749979
>>> 
>>> bool(x)
True
>>> 
>>> y = Vector2d(3, 4)
>>> x == y
False
```

Một vài chú ý:

-   Implement `__iter__` biến object thành iterable đem lại các tác dụng:
    -   Sử dụng trong cú pháp `for...in`
    -   Có thể unpack iterable vào các biến cũng như vào các tuple argument (`*args`) của hàm
    -   Có thể tạo một `list`, `tuple` hay `set` từ một iterable từ constructor `list()`, `tuple()` hay `set()`

-   Format xâu từ object :
    -   Bằng phương thức `__repr__`: `'%r' % obj` hoặc `'{!r}'.format(obj)`
    -   Bằng phương thức `__str__`: `'%s' % obj` hoặc `'{!s}.format(obj)'`

-   Phép so sánh hai tuple được thực hiện nhanh hơn phép so sánh lần lượt từng phần tử

---
### Class Methods vs Static Methods

Python có hai loại phương thức đặc biệt, gọi là *phương thức lớp*, được implements bằng cách sử dụng decorator `@classmethod` và *phương thức tĩnh*, được implement bằng decorator `@staticmethod`. Vậy sự khác biệt giữa chúng là gì?

#### Class Methods

Phương thức lớp là phương thức được thực hiện trên lớp chứ không phải trên các thể hiện riêng lẻ. Điểm đặc biệt của phương thức lớp là thay vì tham số đầu tiên `self` trỏ tới object, nó nhận tham số `cls` trỏ tới class.

Usecase thông dụng nhất của class methods là tạo ra các constructor khác bên cạnh `__init__` (do Python không hỗ trợ overloading functions nên nó cũng không hỗ trợ overloading constructor). Pattern thông dụng khi implement custom constructors là biến đổi tham số và gọi đến constructor `__init__` để khởi tạo đối tượng.

Dưới đây là ví dụ khởi tạo đối tượng bằng hai cách dùng file object hoặc dùng filename:
```python
class Foo(object):

    def __init__(self, file):
        self.file = file

    @classmethod
    def fromfilename(cls, filename):
        file = open(filename, 'rb')
        return cls(file)

>>> with open("test", "rb") as f:    # method 1
        f1 = Foo(f)
>>>
>>> f2 = Foo.fromfilename("test")    # method 2
```

#### Static Methods

Đối lập với `@classmethod`, decorator `@staticmethod` chỉ làm cho phương thức không nhận tham số đầu tiên đặc biệt nào (`self` hay `cls`). Nói cách khác, nó biến phương thức thành một hàm đơn thuần nằm trong phạm vi của class thay vì nằm trong phạm vi của module như thông thường.

Thực tình mà nói, static methods khá là vô dụng :))

---
### Formatted Displays

Người dùng có thể chỉ định cách thức format đối tượng bằng cách dùng hàm  built-in `format()` hoặc phương thức `str.format()`. Cả hai cách này đều gọi đến phương thức `__format(format_spec)__` được implement cho từng đối tượng. Trong đó, `format_spec` là:
-   Tham số thứ hai trong hàm `format`: `format(obj, format_spec)`
-   Các ký tự nằm sau ký tự `:` trong mỗi cặp ngoặc nhọn `{...}` trong xâu `str` trong cú pháp `str.format()`

Ví dụ:

```python
>>> brl = 1/2.43 # BRL to USD currency conversion rate
>>> brl
0.4115226337448559
>>> format(brl, '0.4f')                           # format_spec: 0.4f
'0.4115'
>>> '1 BRL = {rate:0.2f} USD'.format(rate=brl)    # format_spec: 0.2f
'1 BRL = 0.41 USD'
```

#### Placeholder in String Format Method

Cụm `{...}` được dùng trong cú pháp `str.format()` được gọi là placeholder và được dùng để định nghĩa cách thức format một đối tượng. Cú pháp tổng quát của một placeholder là:

```
"{" [field_name] ["!" conversion] [":" format_spec] "}"
```

Trong đó:
-   `field_name` là tên định danh cho placeholder, tên này sau đó được truyền vào hàm format theo cú pháp `.format(field_name=object)
-   `conversion` là phương thức được sử dụng lên object khi format nó sang kiểu xâu, có thể nhận một trong ba giá trị:
    -   `r` -> `repr()`
    -   `s` ->  `str()`
    -   `a`->   `ascii()`
-   `format_spec` là format specifer cho đối tượng

Cú pháp dùng để chỉ định format specifier được gọi là Format Specification Mini-Language, có thể được tìm đọc tại [đây](https://docs.python.org/3.4/library/string.html#format-specification-mini-language), và các use case thường gặp trong việc format xâu dữ liệu tại [đây](https://pyformat.info/).

Mỗi kiểu đều có thể được định nghĩa mini-language riêng dành cho `format_spec`, ví dụ điển hình là `datetime.datetime` có thể in ra thời gian theo những format khác nhau:
```python
>>> from datetime import datetime
>>> now = datetime.now()
>>> format(now, '%H:%M:%S')
'18:49:05'
>>> "It's now {:%I:%M %p}".format(now)
"It's now 06:49 PM"
```

#### Implement User Defined Format Specification

Thông thường, `format()` sẽ fallback về `str()` nên hiện ta vẫn có thể format đối tượng `Vector2d`, nhưng ta chưa thể truyền `format_spec` cho nó.

Tại mục này, ta sẽ bắt tay vào định nghĩa một mini-language cho class `Vector2d` sao cho nó có thể in ra vector theo hai kiểu định dạng:
-    Tọa độ Đề các, bao gồm hoành độ và tung độ
-    Tọa độ cực, bao gồm độ dài và góc của vector

Trong ví dụ dưới đây, ta định nghĩa hàm `__format__` với `format_spec` kết thúc bằng ký tự `p` đại diện cho tọa độ cực, ngược lại là tọa độ Đề-các:

```python
    ...
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
```
Kết quả:

```python
>>> format(Vector2d(1, 1), 'p')
'<1.4142135623730951, 0.7853981633974483>'
>>> format(Vector2d(1, 1), '.3ep')
'<1.414e+00, 7.854e-01>'
>>> format(Vector2d(1, 1), '0.5fp')
'<1.41421, 0.78540>'
>>> format(Vector2d(1, 1), '0.5f')
'(1.00000, 1.00000)'
```

---
### A Hashable Vector2d

Đôi khi ta muốn đưa đối tượng `Vector2d` vào một `set`, hay dùng nó như là key của `dict`. Để làm được điều đó, `Vector2d` phải là hashable.

Tuy nhiên, như đã trình bày ở [Chapter 3](../p2-data-structures/c3-dicts-and-sets.md#generic-mapping-types), do ta đã định nghĩa phương thức `__eq__`, ta cần phải đảm bảo hai điều kiện hashable còn lại phải thỏa mãn, đó là:
-   `Vector2d` là immutable
-   `Vector2d` phải có phương thức `__hash__`

Trước hết, hãy biến `Vector2d` thành immutable:
```python
class Vector2d(object):
...
    def __init__(self, x, y):
        self.__x = float(x)
        self.__y = float(y)

    @property
    def x(self):
        return self.__x
    
    @property
    def foo(self):
        return self.__y
...
```

*Chú ý:*
-   Sử dụng đúng hai dấu gạch dưới phía trước (và tối đa một dấu gạch dưới phía sau) để biến attribute thành private
-   Decorator `@property` biến các attributes thành chỉ đọc và tạo ra getter tương ứng với nó, cách sử dụng nó sẽ được đề cập cụ thể hơn ở [Chương 19](../p6-metaprogramming/c19-dynamic-attributes-and-properties.md)
-   Điều kiện immutability là điều kiện "lỏng", không nhất thiết phải có, cũng không có cách thức chung để kiểm tra một custom object có là immutable hay không. Nhưng việc biến object thành immutable là cần thiết để đảm bảo hash value không bao giờ thay đổi trong vòng đời của đối tượng.

Sau đó, ta implement phương thức `__hash__` với một vài lưu ý:
-   Nên trả về kiểu `int` (tương tự như hàm `id()`)
-   Sử dụng các thuộc tính trong phương thức `__eq__` vì các đối tượng "bằng nhau" nên có cùng giá trị băm
-   Nên sử dụng toán tử xor (`^`) giữa các giá trị băm của các thành phần `x` và `y`

Vậy ta có thể implement phương thức `__hash__` như sau:

```python
...
def __hash__(self):
    return hash(self.x) ^ hash(self.y)
...
```

Như vậy, đối tượng `Vector2d` đã trở thành hashable và có thể đưa vào `set` hay `dict` keys tùy ý rồi.

---
### Private and Protected Attributes in Python

Quy tắc chung để tạo ra một thuộc tính "private" trong Python là **đặt tên thuộc tính bắt đầu bằng hai dấu gạch dưới và kết thúc bằng tối đa một dấu gạch dưới** (`__x` hoặc `__x_`). Quy tắc này không hề đảm bảo thuộc tính là private tuyệt đối như khi dùng từ khóa `private` trong Java. Nó chỉ có chức năng ngăn chặn việc vô tình ghi đè giá trị của nó mà thôi, khi lập trình viên sử dụng thuộc tính của đối tượng mà bắt đầu bằng dấu `__`, anh ta cần hiểu rằng mình đang truy cập vào một thuộc tính private và không nên chỉnh sửa nó.

Nếu class `Dog` và class kế thừa nó là `Beagle` tình cờ cùng sử dụng một thuộc tính private là `__mood` (class này không biết đến sự tồn tại của thuộc tính `__mood` của class kia). Để ngăn chặn xung đột trong việc sử dụng biến, thuộc tính `__mood` được trình thông dịch của Python đổi tên thành `_<classname>__mood`. Như vậy, class `Beagle` tránh được việc truy cập nhầm tới thuộc tính `__mood` của class `Dog` và ngược lại. Tính năng này gọi là *name mangling*, được thiết kế nhằm tránh việc truy cập sai biến không chủ đích chứ không nhằm mục đích ngăn chặn việc cố tình làm sai.

Tất nhiên rằng, nếu ai đó biết được điều này, họ hoàn toàn có thể truy cập đến thuộc tính "private" để thay đổi nó (VD: `Vector2d(3, 4)._Vector2d__x = 7`). Tuy nhiên nếu họ làm điều này, họ không thể đổ lỗi cho ai nếu có vấn đề xảy ra sau đó.

Tính năng name mangling không làm vừa lòng tất cả các Pythonistas. Đơn cử như cú pháp `self.__x`, nhiều người không thích nó và chuộng việc sử dụng chỉ một dấu gạch dưới trước tên biến hơn (`self._x`). Cú pháp một dấu gạch dưới trước tên biến không có ý nghĩa đặc biệt đối với trình thông dịch của Python, nó cũng không ngăn chặn việc xung đột thuộc tính nội bộ giữa hai class có quan hệ thừa kế, tuy nhiên nó mang ý nghĩa mạnh mẽ đối với các lập trình viên Python rằng: "Không sử dụng thuộc tính này bên ngoài định nghĩa lớp".

Tóm lại, "private" attributes trong Python bắt đầu bằng hai dấu gạch dưới, "protected" attributes bắt đầu bằng một dấu gạch dưới. Đây chỉ là convention được thống nhất giữa cộng đồng người lập trình Python và thực tế chúng đều là publicly accessible.

---
### Saving Space with the __slots__ Class Attribute

Theo mặc định, Python lưu trữ các thuộc tính của một đối tượng trong thuộc tính `__dict__`. Mỗi `__dict__` sinh ra một bảng băm giúp truy cập thuộc tính nhanh chóng, nhưng lại gây lãng phí tài nguyên bộ nhớ nếu chương trình tạo ra rất nhiều đối tượng mà có ít thuộc tính.

Giải pháp cho vấn đề được đề cập đến ở trên đó là sử dụng thuộc tính lớp `__slots__` để lưu trữ tất cả các thuộc tính của đối tượng trong một kiểu tuple thay vì dict, giúp cải thiện hiệu năng tính toán đáng kể trong trường hợp kể trên.

**Nhược điểm:**
-   `__slots__` không được thừa kế cho lớp con
-   Phải khai báo tất cả các thuộc tính của instance cho `__slots__`, không hỗ trợ các thuộc tính động
-   Phải để `__weakref__` bên trong `__slots__` khi muốn đối tượng có thể trỏ đến được bởi weak references

Nếu class của bạn không có quá nhiều instances, việc dùng `__slots__` là không đáng cho những sự đánh đổi kể trên. Hãy cân nhắc kỹ trước khi sử dụng.

---
### Overriding Class Attributes

Thuộc tính lớp là thuộc tính mặc định cho các đối tượng của lớp. Mỗi lần một đối tượng mới được tạo ra, nó sẽ có một tham chiếu tới giá trị lưu bởi thuộc tính này. Trong class `Vector2d`, thuộc tính lớp duy nhất được định nghĩa là `typecode`:

```python
>>> x = Vector2d(1, 2)
>>> x.typecode
'd'
```
Ta có thể gán lại giá trị cho thuộc tính lớp trên đối tượng mà không làm thay đổi giá trị mặc định:

```python
>>> x.typecode = 'f'
>>> Vector2d.typecode
'd'
```
Tuy nhiên, nếu thuộc tính lớp là mutable và ta sửa thuộc tính lớp từ đối tượng thì giá trị mặc định cũng thay đổi theo:

```python
>>> Vector2d.typecode = []
>>> x = Vector2d(3, 4)
>>> x.typecode.append(3)
>>> Vector2d.typecode
[3]
```
Điều này giống hệt với vấn đề xảy ra đối với tham số mặc định của phương thức mà ta đã đề cập đến ở [Chương 8](./c8-oop-properties.md#mutable-types-as-parameter-defaults-bad-idea)

Vậy `typecode` là gì và tại sao lại định nghĩa nó trong class `Vector2d`? Câu trả lời là để ta có thể convert object ra dạng biểu diễn bytes thông qua hàm `bytes()` bằng cách implement phương thức `__bytes__` như sau:
```python
from array import array
class Vector2d:
    typecode = 'd'
    ...
    # Export vector to bytes
    def __bytes__(self):
        return (bytes([ord(self.typecode)]) +
                bytes(array(self.typecode, self)))

    # Import vector from bytes
    @classmethod
    def frombytes(cls, octets):
        typecode = chr(octets[0])
        memv = memoryview(octets[1:]).cast(typecode)
    return cls(*memv)

>>> v1 = Vector2d(1.1, 2.2)
>>> dumpd = bytes(v1)
>>> dumpd
b'd\x9a\x99\x99\x99\x99\x99\xf1?\x9a\x99\x99\x99\x99\x99\x01@'
>>> len(dumpd)
17
``` 

Ở đây, `typecode` là `d`, ám chỉ rằng các thành phần của vector sẽ được thể hiện bằng kiểu số thực `double` (8-byte, double precision float) khi export ra bytes. Việc thay đổi `typecode` sẽ làm thay đổi độ chính xác của kiểu số thực khi export ra bytes, ví dụ `Vector2d.typecode = 'f'` sẽ export các thành phần ra kiểu `float` (4-byte, single precision).

Tuy nhiên, ta không nên thay đổi trực tiếp thuộc tính lớp, do giá trị đó là mặc định của người viết, họ không muốn người dùng tùy ý thay đổi nó, cách làm hợp lý nhất là tạo lớp mới thừa kế lớp này và cập nhật lại thuộc tính lớp trên lớp con:

```python
>>> class ShortVector2d(Vector2d):
...     typecode = 'f'
...
>>> v2 = ShortVector2d(1.1, 2.2)
>>> dumpf = bytes(v2)
>>> dumpf
b'f\xcd\xcc\x8c?\xcd\xcc\x0c@'
>>> len(dumpd)
9
```

---
### Summary

Chương này trình bày cách implement một Pythonic `Vector2d` với các tính năng như export đối tượng vector qua các phương thức như `str`, `repr`, `bytes` hay `format`, so sánh các vector với nhau, tính độ dài và góc của vector, và biến vector thành một hashable object.

Format Specification Mini-language cũng được giới thiệu thông qua ví dụ về một mini-language đơn giản.

Tiếp đến, thuộc tính `__slots__` cũng được giới thiệu như là một cách để tiết kiệm bộ nhớ khi số lượng đối tượng tăng lên.

Cuối cùng, bạn đọc đã được làm quen với cách thức sử dụng và ghi đè phương thức lớp một cách hợp lý.

---
### Soapbox

> Mục soapbox trong chương này đưa ra những tranh luận rất hay về quan điểm thiết kế encapsulation của Python so sánh với Java. Bạn đọc nên đọc và nếu có thể, hãy đóng góp bản dịch cho phần này để tài liệu trở nên hoàn thiện hơn. Xin chân thành cảm ơn.