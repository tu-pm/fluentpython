# Context Manager and else Blocks

## else Blocks Beyond if

Mệnh đề `else` có thể được dùng cùng với các mệnh đề `for`, `while` và `try`

*   `for`, `while`: Khối `else` chỉ được chạy khi vòng lặp  không bị `break` giữa chừng
*   `try`: Khối `else` chỉ được chạy khi không có ngoại lệ nào xảy ra trong `try`

Trong tất cả các trường hợp, mệnh đề `else` đều bị bỏ qua nếu như có một ngoại lệ, một mệnh đề `return`, `break` hay `continue` khiến cho luồng điều khiển bị nhảy ra bên ngoài khối chương trình chính.

Sử dụng `else` sau vòng lặp giúp code trở nên dễ đọc hơn và tránh khỏi việc phải tạo ra một cờ điều khiển hoặc một lệnh `if` khác trong vòng lặp. Ví dụ đoạn code này:

```python
found = False
for item in my_list:
    if item.flavor == 'banana':
        found = True        
        break
if not found:
    raise ValueError('No banana flavor found!')
```

có thể được thay thế bằng đoạn code sử dụng `else` như sau:

```python
for item in my_list:
    if item.flavor == 'banana':
        break
else:
    raise ValueError('No banana flavor found!')
```

Còn trong trường hợp `try...except`, mệnh đề `else` có vẻ là dư thừa nhưng thực ra nó vẫn rất hữu ích. Trước hết, ta sẽ bắt đầu với luồng xử lý ngoại lệ trong Python:

```python
try:
    # try executing some code...
    pass
except Exception as e:
    # if an exception occurs, do this
    pass
else:
    # run this if no exception occurs
finally:
    # always run this at the end
```

=>   Khối `else` là vị trí hợp lý nhất để đặt một đoạn code mà chỉ chạy nếu không có ngoại lệ nào xảy ra, bất kể việc xử lý ngoại lệ trong khối `except` có thể đưa logic xử lý quay lại luồng xử lý chính.

Trong Python, `try/except` được sử dụng nhiều trong kiểm soát luồng, chứ không chỉ là xử lý lỗi. Hai triết lý lập trình đối lập giữa Python và các ngôn ngữ khác như C:

*   Python: EAFP - Easier to ask for forgiveness than permission
*   C: LBYL - Look before you leap

Xem thêm về hai triết lý này trong sách fluent python, trang 451.

## Context Managers and with Blocks

Context manager objects được tạo ra để quản lý câu lệnh `with`, giống như cách iterators quản lý câu lệnh `for`.

Context management sơ khai được thực hiện bởi khối `try...finally`.

    *   Khối `try`:
        *    (1) "set up context" (mở file, kết nối cơ sở dữ liệu, ...)
        *    (2) "do something in the context".
    *   Khối `finally`: 
        *   "tear down context" (đóng file, đóng kết nối csdl, ...)
        *   Luôn được thực hiện, ngay cả khi luồng xử lý bị ngắt bởi ngoại lệ, bởi lệnh `return` hay cú pháp `sys.exit()`.

Một cách trực quan, cú pháp này được biểu diễn như sau:

```python
ctx = Ctx()
try:
    obj = ctx.__enter__()    # set up context
    do_something(obj)
finally:
    ctx.__exit__()  # tear down context
```

*Chú ý:*

*   Quá trình tạo và hủy context được đóng gói trong hai phương thức `__enter__` và `__exit__` của lớp `Ctx`, lớp này chính là một context manager
*   `obj` là không phải là thể hiện của `Ctx`, nó là đối tượng trả về của phương thức `Ctx.__enter__()`. Ví dụ như khi mở file, ta cần nhận về một đối tượng file để thao tác trên nó, nhưng trong hầu hết các trường hợp khác, ta không cần lấy về đối tượng này

Và khối `try...finally` trên tương đương với một khối `with` đơn giản hơn rất nhiều:

```python
with Ctx() as obj:
    do_something()
```

Như vậy, quá trình thiết kế và sử dụng context manager thông qua hai bước:

    *   Thiết kế context manager: Một lớp implement context manager protocol với hai phương thức `__enter__` và `__exit__`
    *   Sử dụng context manager với câu lệnh `with`

### Designing A Context Manager

#### Context Manager Class Requirement

Để định nghĩa một lớp tuân theo context manager protocol, ta chỉ cần định nghĩa hai phương thức `__enter__` và `__exit__`. Chữ ký bắt buộc của hai lớp này là:

    *   `__enter__(self)`: Chỉ nhận tham số `self`
    *   `__exit__(self, exc_type, exc_value, traceback)`:
        *   Cả ba tham số sau đều là `None` nếu không có ngoại lệ xảy ra
        *   `exc_type`: Exception class
        *   `exc_value`: Exception instance
        *   `traceback`: traceback object

#### Example

Ví dụ: Tạo context manager để tạo bảng khi kết nối đến cơ sở dữ liệu và xóa nó khi kết thúc kết nối.

***Bước 1: Implement theo context manager protocol***

```python
from sqlite3 import connect

class temptable:
	"""A context manager that create and destroy a table named 'points'
	each time it is called."""
	
	def __init__(self, cur):
		self.cur = cur

	def __enter__(self):
		print('__enter__')
		self.cur.execute('create table points(x int, y int)')

	def __exit__(self, exc_type, exc_value, traceback):
		print('__exit__')
		self.cur.execute('drop table points')

# 'connect' is the built-in database context manager
with connect('test.db') as conn: 	
	cur = conn.cursor()
	# 'temptable' is the previously defined context manager
	with temptable(cur):
		cur.execute('insert into points (x, y) values (1, 2)')
		cur.execute('insert into points (x, y) values (3, 4)')
		for row in cur.execute('select x, y from points')
			print(row)
```

    Output:
    __enter__
    (1, 2)
    (3, 4)
    __exit__

***Bước 2: Sử dụng generator function***

```python
def temptable(cur):
	cur.execute('create table points(x int, y int)')
	print('created table')
	yield
	cur.execute('drop table points')
	print('dropped table')


class ContextManager:

	def __init__(self, cur):
		self.cur = cur

	def __enter__(self):
		self.gen = temptable(self.cur)
		next(self.gen)
	
	def __exit__(self):
		next(self.gen, None)

with connect('test.db') as conn:
	cur = conn.cursor()
	with ContextManager(cur):
		cur.execute('insert into points (x, y) values (1, 2)')
		cur.execute('insert into points (x, y) values (3, 4)')
		for row in cur.execute('select x, y from points')
			print(row)
```

    Output:
    created table
    (1, 2)
    (3, 4)
    droped table

*Chú ý:*

*   Tham số thứ hai của `next` là `default` - giá trị trả về mặc định thay vì việc tung `StopIteration` exception khi lấy hết item từ iterator
*   Tại sao dùng generator function? Hồi sau sẽ rõ

Lớp `ContextManager` đang được hard-code với `temptable`, ta sẽ khiến nó có thể khởi tạo từ bất kỳ generator function nào như sau:

***Bước 3: Tổng quát hóa lớp ContextManager***

```python
class ContextManager:

	def __init__(self, gen):
		# accept any generator function
		self.gen = gen

	def __call__(*args, **kwargs):
		self.args, self.kwargs = args, kwargs
		return self

	def __enter__(self):
		# create a generator instance from abitrary arguments
		self.gen_inst = self.gen(*self.args, **self.kwargs)
		next(self.gen_inst)

	def __exit__(self):
		next(self, gen_inst, None)


def temptable(cur):
	# ...
temptable = ContextManager(temptable)

# ...
```

*Chú ý:*

*   Tại sao lại implement phương thức `__call__`? Vì nó biến đối tượng của `ContextManager` thành callable -> Cú pháp `tempatable = ContextManager(temptable)` sẽ biến `temptable` thành một đối tượng `ContextManager` -> `temptable(cur)` lưu `cur` vào `temptable.cur` để sử dụng sau đó trong phương thức `__enter__`
*   Tại sao phải thay đổi `temptable` để mọi thứ thành phức tạp vậy? DECORATOR!!!

***Bước 4: ContextManager decorator***

```python
class ContextManager:
    # ...

@ContextManager
def temptable(cur)
    # ...
```

Như vậy, áp `@ContextManager` lên bất kỳ một generator function nào, hàm đó đều trở thành một context manager (Cool!!). Và thực ra, ta không cần phải viết lớp `ContextManager` làm gì, vì trong thư viện chuẩn đã có sẵn lớp này rồi, đó là `contextlib.contextmanager`. Chỉ cần thay đổi định dạng của `temptable` một chút là ta có thể dùng nó với decorator này:

```python
from contextlib import contextmanager

@contextmanager
def temptable(cur):
	cur.execute('create table points(x int, y int)')
	print('created table')
	try:
		yield
	finally:
		cur.execute('drop table points')
		print('dropped table')
```

### The contextlib Module

*   Tạm thời chuyển luồng ra chuẩn thành file `f`:

    ```python
    with contextlib.redirect_stdout(f):
        do_something()
    ```

*   Nếu đối tượng nào đó có phương thức `close()`, ngụ ý rằng nên "đóng" nó lại khi không dùng đến nữa => Tự động đóng nó bằng context manager `closing`:

    ```python
    with contextlib.closing(closable_obj):
        do_something()
    ```

*   Bỏ qua một vài ngoại lệ nào đó trong một xử lý:

    ```python
    with contextlib.suppress(*exceptions):
        do_something()
    ```

*   Tự tạo một context manager từ một generator function:

    ```python
    @contextlib.contextmanager
    def managed_resource(*args, **kwargs):
        resource = acquire_resource(*args, **kwargs)
        try:
            yield resource
        finally:
            release_resource(resource)

    >>> with managed_resource(args) as resource:
    ...     do_something()
    ```

    *   Giá trị được `yield` ra là giá trị nhận về sau từ khóa `as` trong cấu trúc `with...as`
    *   `acquire_resource` là thao tác set up context
    *   `release_resource` là thao tác tear down context
