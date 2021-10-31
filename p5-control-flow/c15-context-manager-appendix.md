## Appendix: Design A Context Manager

Trong thời gian đọc cuốn Fluent Python, mình có xem được một bài thuyết trình về Context Manager tuyệt vời: [What Does It Take To Be An Expert At Python?](https://www.youtube.com/watch?v=7lmCu8wz8ro&t=5845s).

Trong bài nói trên, tác giả đưa ra ví dụ implement một context manager đơn giản có khả năng tạo bảng tạm mỗi khi kết nối tới cơ sở dữ liệu và xóa nó khi kết thúc phiên làm việc. Ví dụ này sẽ dẫn bạn đi qua các bước để thiết kế một context manager tổng quát, bao gồm:
1.  Thiết kế theo Context Manager Protocol
2.  Sử dụng generator cho context manager
3.  Tổng quát hóa context manager
4.  Sử dụng `@contextmanager` decorator

Ví dụ này hé lộ những gì hay nhất về context manager cũng như cho ta thấy cách implement context manager một cách hiệu quả và *pythonic* nhất.

---
### Take 1: Context Manager Protocol

Để định nghĩa một lớp tuân theo context manager protocol, ta chỉ cần định nghĩa hai phương thức `__enter__` và `__exit__`. Chữ ký của hai phương thức này là:
-   `__enter__(self)`: Chỉ nhận tham số `self`
-   `__exit__(self, exc_type=None, exc_value=None, traceback=None)`:
    -   `exc_type`: Exception class
    -   `exc_value`: Exception instance
    -   `traceback`: traceback object

Dưới đây là bản triển khai đầu tiên sử dụng context manager protocol:

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

with connect('test.db') as conn:     
    cur = conn.cursor()
    with temptable(cur):
        cur.execute('insert into points (x, y) values (1, 2)')
        cur.execute('insert into points (x, y) values (3, 4)')
        for row in cur.execute('select x, y from points'):
            print(row)
```

Output:
```
__enter__
(1, 2)
(3, 4)
__exit__
```

---
### Take 2: Use Generator Function

Ta thấy `__exit__` luôn được thực thi sau `__enter__`, ta có thể implement cơ chế enforce thứ tự của chuỗi hành động thông qua generator như sau:

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
        for row in cur.execute('select x, y from points'):
            print(row)
```

Output:
```
created table
(1, 2)
(3, 4)
droped table
```

Bạn có thấy việc dùng generator ở đây khá tricky và không có lý do nào rõ ràng để làm như thế? Hãy tiếp tục theo dõi nhé.

---
### Take 3: Generalized Context Manager

Lớp `ContextManager` đang được hard-code với `temptable`, ta sẽ khiến nó có thể khởi tạo từ bất kỳ generator function nào như sau:

```python
def temptable(cur):
    cur.execute('create table points(x int, y int)')
    print('created table')
    yield
    cur.execute('drop table points')
    print('dropped table')


class ContextManager:
    def __init__(self, gen):
        # accept any generator function
        self.gen = gen

    def __call__(*args, **kwargs):
        self.args, self.kwargs = args, kwargs
        return self

    def __enter__(self):
        self.gen_inst = self.gen(*self.args, **self.kwargs)
        next(self.gen_inst)

    def __exit__(self):
        next(self, gen_inst, None)

temptable = ContextManager(temptable)

with connect('test.db') as conn:
    cur = conn.cursor()
    with temptable(cur):
        cur.execute('insert into points (x, y) values (1, 2)')
        cur.execute('insert into points (x, y) values (3, 4)')
        for row in cur.execute('select x, y from points'):
            print(row)
```

*Chú ý:*
-   Đối tượng `tt` của lớp `ContextManager` giờ có tham chiếu tới một generator bất kỳ, và nó cũng là một callable object nữa
-   Cú pháp `temptable = ContextManager(temptable)` có gợi nhớ cho bạn về decorator?

---
### Take 4: Context Manager Decorator

Ta hoàn toàn có thể sử dụng `ContextManager` như là decorator của `temptable` như sau:

```python
class ContextManager:
    def __init__(self, gen):
        # accept any generator function
        self.gen = gen

    def __call__(*args, **kwargs):
        self.args, self.kwargs = args, kwargs
        return self

    def __enter__(self):
        self.gen_inst = self.gen(*self.args, **self.kwargs)
        next(self.gen_inst)

    def __exit__(self):
        next(self, gen_inst, None)

@ContextManager
def temptable(cur)
    cur.execute('create table points(x int, y int)')
    print('created table')
    yield
    cur.execute('drop table points')
    print('dropped table')
```

*Yay*, giờ chỉ cần áp `@ContextManager` lên bất kỳ một generator function nào, hàm đó đều trở thành một context manager. Ta còn có thể đóng nó vào thư viện cho người khác sử dụng nữa ấy chứ.

Khoan, thực tế trong thư viện chuẩn đã có một lớp tương tự `ContextManager` rồi, nó chính là `contextlib.contextmanager`. Và ta chỉ cần chỉnh sửa một chút code để có thể xây dựng context manager từ generator function mà thôi:

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

Như vậy, quá trình xây dựng lớp `ContextManager` tổng quát đã khiến ta nhận ra rằng mình vừa phát minh lại cái bánh xe. Nó vừa giúp ta có thêm những cái nhìn sâu sắc hơn về việc xây dựng context manager, lại vừa giúp ta khám phá thêm một cách định nghĩa context manager một cách dễ dàng.
