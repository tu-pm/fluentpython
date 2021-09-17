# A Pythonic Object

"Never, ever use two leading underscores. This is annoyingly private".

Nhờ vào khái niệm Data Model, các đối tượng user-defined có thể biểu hiện tự nhiên như một đối tượng thuộc kiểu built-in. Chapter này sẽ đề cập đến việc làm thế nào để thực hiện được điều này.

## Object Representations

Hai cách chủ yếu được sử dụng để lấy ra thông tin đại diện cho một object bất kỳ dưới dạng một xâu trong Python:

-   **`repr()`**: Trả về những thứ mà developers cần
-   **`str()`**: Trả về những thứ mà người dùng cần

Để sử dụng hai hàm này với một object, nó cần được implement hai phương thức tương ứng là **`__repr__`** và **`__str__`**.

Hai cách khác đó là **`bytes()`** và **`format()`**, ví dụ về cách sử dụng chúng được đề cập ở những phần sau.

## Vector Class Redux

Dưới đây là một ví dụ về Pythonic Vector2d class, vector này có thể được:

-   In ra với lệnh `print`
-   Unpack thành một tuple chứa hoành độ và tung độ của vector
-   Tính độ dài với lệnh **`abs()`**
-   Đánh giá tính đúng sai với lệnh **`bool()`** (Vector là False nếu và chỉ nếu nó có độ dài bằng 0)
-   So sánh bằng nhau với vector khác bằng cú pháp **`==`**

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
		return math.hypot(tuple(self))

	def __bool__(self):
		return bool(abs(self))
```

Một vài chú ý:

-   Implement **`__iter__`** biến object thành iterable đem lại rất nhiều lợi ích:
    -   Sử dụng trong cú pháp `for...in`
    -   Có thể unpack iterable vào các biến cũng như vào các tham số (`*self`) của hàm
    -   Có thể tạo một `list`, `tuple` hay `set` từ một iterable từ constructor `list()`, `tuple()` hay `set()`

-   Format xâu từ object :
    -   Bằng phương thức `__repr__`: `'%r' % obj` hoặc `'{!r}'.format(obj)`
    -   Bằng phương thức `__str__`: `'%s' % obj` hoặc `'{!s}.format(obj)'`

-   Phép so sánh hai tuple được thực hiện nhanh hơn phép so sánh lần lượt từng phần tử

## Class Methods vs Static Methods

Python tồn tại hai khái niệm độc lập, phương thức lớp, được implements bằng cách sử dụng decorator **`@classmethod`** và phương thức tĩnh, được implement bằng decorator **`@staticmethod`**, sự khác biệt giữa chúng là gì?

**Class Methods**

Phương thức lớp là phương thức được thực hiện trên lớp chứ không phải trên các thể hiện riêng lẻ.

Usecase thông dụng nhất của class methods là tạo ra các constructor khác bên cạnh `__init__` (do Python không hỗ trợ overloading functions nên nó cũng không hỗ trợ overloading constructor). Khi viết một constructor khác `__init__`, hãy biến các tham số "chưa chuẩn" này thành các tham số "chuẩn" và khởi tạo đối tượng mới từ các tham số chuẩn này bên trong constructor. Ví dụ:

    ```python
    class Foo(object):
	
	    def __init__(self, file):
		    self.file = file

	    @classmethod
	    def fromfilename(cls, filename):
		    file = open(filename, 'rb')
		    return cls(file)
    ```

**Static Methods**

Đối lập với `@classmethod`, decorator `@staticmethod` chỉ khiến phương thức không nhận tham số đầu đặc biệt nào (self hay cls). Nói cách khác, nó biến phương thức thành một hàm đơn thuần nằm trong phạm vi của class thay vì nằm trong phạm vi của module như thông thường.

Thực tình mà nói, static methods khá là vô dụng :))

## Formatted Displays

Hàm built-in **`format()`** và phương thức **`str.format()`** thực hiện format xâu với từng kiểu tham số khác nhau bằng cách gọi đến hàm **`__format(format_spec)__`** được implement cho từng kiểu. Trong đó, `format_spec` có thể là:

-   Tham số thứ hai trong hàm **`format`**: `format(obj, format_spec)`
-   Các ký tự nằm sau ký tự '**`:`**' trong mỗi cặp ngoặc nhọn '**`{...}`**' trong xâu **`str`** trong cú pháp **`str.format()`**

Ví dụ:

```python
>>> brl = 1/2.43 # BRL to USD currency conversion rate
>>> brl
0.4115226337448559
>>> format(brl, '0.4f') #1
'0.4115'
>>> '1 BRL = {rate:0.2f} USD'.format(rate=brl) #2
'1 BRL = 0.41 USD'
```

### Placeholder in String Format Method

Cụm `{...}` được dùng trong cú pháp `str.format()` được gọi là placeholder và được dùng để định nghĩa cách thức format một đối tượng. Cú pháp tổng quát của một placeholder là:

    ```python
    "{" [field_name] ["!" conversion] [":" format_spec] "}"
    ```

Trong đó:

-   `field_name` là tên định danh cho placeholder, tên này sau đó được truyền vào hàm format theo cú pháp `.format(field_name=object)
-   `conversion` là phương thức được sử dụng lên object khi format nó sang kiểu xâu, có thể nhận một trong ba giá trị:
    -   `r` -> `repr()`
    -   `s` ->  `str()`
    -   `a`->   `ascii()`
-   `format_spec` là format specifer cho kiểu được sử dụng, nó lại được cấu thành bởi cú pháp:
        ```python
        [[fill]align][sign][#][0][width][,][.precision][type]
        ```        
    -   `fill`: Một ký tự bất kỳ điền vào các vị trí trống khi format xâu, mặc định là dấu cách
    -   `align`: Cách căn lề, bao gồm "<" (trái), ">" (phải), "^" (giữa), "=" (đều hai bên)
    -   `sign`: Cách thức thêm dấu cho dữ liệu kiểu số, bao gồm "+" (thêm dấu cho cả số âm và dương), "-" (chỉ thêm dấu cho số âm), " " (thêm dấu " " vào trước số dương và "-" vào trước số âm)
    -   `#`: chỉ định ra định dạng conversion khác cho xâu
    -   `,`: Thêm dấu ',' để ngăn cách các cụm ba số trong hệ số thập phân
    -   `with`: Kích thước nhỏ nhất của khung
    -   `precision`: Độ chính xác của số thập phân

Một vài ví dụ:

```python
>>> format(42, 'b')
'101010'
>>> format(2/3, '.1%')
'66.7%'
>>> from datetime import datetime
>>> now = datetime.now()
>>> format(now, '%H:%M:%S')
'18:49:05'
>>> "It's now {:%I:%M %p}".format(now)
"It's now 06:49 PM"
```

Cú pháp dùng để chỉ định format specifier được gọi là Format Specification Mini-Language, có thể được tìm đọc tại [đây](https://docs.python.org/3.4/library/string.html#format-specification-mini-language)

Các use case thường gặp trong việc format xâu dữ liệu tại [đây](https://pyformat.info/)

### Implement User Defined Format Specification

Ta có thể định nghĩa cách format cho một đối tượng kiểu `Vector2d` bằng cách format từng thành phần tọa độ của nó như sau:

```python
...

def __format__(self, fmt_spec=''):
    components = (format(c, fmt_spec) for c in self)
    return '({}, {})'.format(*components) 
```

Cách thứ 2 nâng cao hơn, ta sẽ định nghĩa format vector theo tọa độ cực **`(r, theta)`** nếu như **`format_spec`** kết thúc bằng ký tự **`p`**:

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
```
## A Hashable Vector2d

Điều kiện để một đối tượng là `hashable` là:

-   Có phương thức `__eq__`
-   Có phương thức `__hash__`
-   Là immutable

Biến thể hiện của Vector2d thành immutable:

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
-   Decorator `@property` biến các attributes thành chỉ đọc và tạo ra getter tương ứng với nó, cách sử dụng nó sẽ được đề cập cụ thể hơn ở chương 19

Bây giờ ta implement phương thức `__hash__` với một vài chú ý:

-   Nên trả về kiểu **`int`**
-   Sử dụng các thuộc tính trong phương thức `__eq__` vì các đối tượng "bằng nhau" nên có cùng giá trị băm
-   Nên sử dụng toán tử xor (**`^`**) giữa các giá trị băm của các thành phần

Vậy ta có thể implement phương thức này như sau:

```python
...
def __hash__(self):
		return hash(self.x) ^ hash(self.y)
...
```

Done!

## Private and Protected Attributes in Python

Python không có cơ chế tạo ra thuộc tính private tuyệt đối như từ khóa `private` trong Java. Thuộc tính private trong Python không 100% "private", nó chỉ có chức năng ngăn chặn việc overwriting thuộc tính một cách không chủ đích.

Ví dụ ta có một class `Dog` và một class kế thừa nó là `Beagle`, cả hai tình cờ cùng sử dụng một thuộc tính nội bộ là `__mood` (class này không biết đến sự tồn tại của thuộc tính `__mood` của class kia). Để ngăn chặn xung đột trong việc sử dụng biến, thuộc tính `__mood` được trình thông dịch của Python đổi tên thành `_classname__mood`. Như vậy, class `Beagle` tránh được việc truy cập nhầm tới thuộc tính `__mood` của class `Dog` và ngược lại . Tính năng này gọi là *name mangling*, được thiết kế nhằm tránh việc truy cập sai biến không chủ đích chứ không nhằm mục đích ngăn chặn việc cố tình làm sai.

Tất nhiên rằng, nếu ai đó biết được điều này, họ hoàn toàn có thể truy cập đến thuộc tính "private" để thay đổi nó (VD: `Vector2d(3, 4)._Vector2d__x = 7`). Tuy nhiên nếu họ làm điều này, họ không thể đổ lỗi cho ai nếu có vấn đề xảy ra sau đó.

Tính năng name mangling không làm vừa lòng tất cả các Pythonistas. Đơn cử như cú pháp `self.__x`, nhiều người không thích nó và chuộng việc sử dụng chỉ một dấu gạch dưới trước tên biến hơn (`self._x`). Cú pháp một dấu gạch dưới trước tên biến không có ý nghĩa đặc biệt đối với trình thông dịch của Python, nó cũng không ngăn chặn việc xung đột thuộc tính nội bộ giữa hai class có quan hệ thừa kế, tuy nhiên nó mang ý nghĩa mạnh mẽ đối với các lập trình viên Python rằng: "Không sử dụng thuộc tính này bên ngoài định nghĩa lớp".

Tóm lại, "private" attributes trong Python bắt đầu bằng hai dấu gạch dưới, "protected" attributes bắt đầu bằng một dấu gạch dưới. Đây chỉ là convention được thống nhất giữa cộng đồng người lập trình Python và thực tế chúng đều là publicly accessible.

## Saving Space with the __slots__ Class Attribute

Theo mặc định, Python lưu trữ các thuộc tính của một thể hiện trong `__dict__`. Việc sử dụng `__dict__` tiêu tốn nhiều tài nguyên bộ nhớ bởi nó được cài đặt trên một kiểu cấu trúc dữ liệu bảng băm giúp cho phép khả năng truy cập nhanh chóng. Điều này gây ra khó khăn rất lớn nếu như chương trình của ta thao tác với một số lượng lớn các đối tượng có chứa ít thuộc tính.

Giải pháp cho vấn đề được đề cập đến ở trên đó là sử dụng thuộc tính lớp **`__slots__`** lưu trữ tất cả các thuộc tính của đối tượng trong một kiểu tuple thay vì dict, giúp cải thiện hiệu năng tính toán đáng kể khi có nhiều instance cùng chạy một lúc.

**Nhược điểm:**

-   **`__slots__`** không được thừa kế cho lớp con
-   Phải khai báo tất cả các thuộc tính của instance cho **`__slots__`**

## Overriding Class Attributes

Thuộc tính lớp là thuộc tính mặc định cho các đối tượng của lớp. Mỗi lần một đối tượng mới được tạo ra, nó sẽ có một tham chiếu tới giá trị lưu bởi thuộc tính này:

```python
>>> x = Vector2d(1, 2)
>>> x.typecode
'd'
```
Ta có thể gán lại giá trị cho thuộc tính lớp của đối tượng mà không làm thay đổi giá trị mặc định:

```python
>>> x.typecode = 'f'
>>> Vector2d.typecode
'd'
```
Tuy nhiên, nếu thuộc tính lớp là immutable và ta sửa thuộc tính lớp từ đối tượng thì giá trị mặc định cũng thay đổi theo:

```python
>>> Vector2d.typecode = []
>>> x = Vector2d(3, 4)
>>> x.typecode.append(3)
>>> Vector2d.typecode
[3]
```
Điều này giống hệt với vấn đề xảy ra đối với tham số mặc định của phương thức mà ta đã đề cập đến ở trên.

Tuy nhiên, vấn đề chính mà ta cần xem xét ở mục này đó là cách thức thay đổi thuộc tính lớp. Ta hoàn toàn có thể thay đổi bằng cách sử dụng tên lớp: `Vector2d.typecode = 'f'`. Mặc dù vậy, bởi lẽ thuộc tính lớp là giá trị mặc định cho lớp, người viết ra lớp này có thể không mong muốn việc thay đổi tùy tiện thuộc tính lớp như thế. Cách làm phổ biến hơn cả đó là subclass lớp này và thay đổi thuộc tính lớp ở lớp con:

```python
>>> class ShortVector2d(Vector2d):
...         typecode = 'f'
...
>>> sv = ShortVector2d(1, 2)
>>> sv
ShortVector2d(1.0, 2.0)
```
