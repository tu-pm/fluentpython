## Chapter 15: Context Manager and else Blocks

---
### Table of Contents

- [Chapter 15: Context Manager and else Blocks](#chapter-15-context-manager-and-else-blocks)
  - [Table of Contents](#table-of-contents)
  - [Do This, Then That: else Blocks Beyond if](#do-this-then-that-else-blocks-beyond-if)
  - [Context Managers and with Blocks](#context-managers-and-with-blocks)
  - [The contextlib Module](#the-contextlib-module)
  - [Using @contextmanager](#using-contextmanager)
  - [Summary](#summary)
  - [Soapbox](#soapbox)


---
### Do This, Then That: else Blocks Beyond if

Mệnh đề `else` có thể được dùng cùng với các mệnh đề `for`, `while` và `try`:
-   `for`, `while`: Khối `else` chỉ được chạy khi vòng lặp  không bị `break` giữa chừng
-   `try`: Khối `else` chỉ được chạy khi không có ngoại lệ nào xảy ra trong `try`

Trong tất cả các trường hợp, mệnh đề `else` đều bị bỏ qua nếu như có ngoại lệ, hoặc có một mệnh đề `return`, `break` hay `continue` khiến luồng điều khiển bị nhảy ra bên ngoài khối chương trình chính.

Sử dụng `else` sau vòng lặp giúp code trở nên dễ đọc hơn và tránh khỏi việc phải tạo ra một cờ điều khiển hoặc một lệnh `if` khác trong vòng lặp. 

Ví dụ đoạn code này:

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

Trong khối `try/except`, mệnh đề `else` nhìn có vẻ dư thừa nhưng thực ra nó vẫn rất hữu ích:

```python
try:
    # try executing some code...
    pass
except Exception as e:
    # if an exception occurs, do this
    pass
else:
    # run this if no exception occurs
    pass
finally:
    # always run this at the end
    pass
```

=>   Khối `else` là vị trí hợp lý nhất để đặt một đoạn code mà chỉ chạy nếu không có ngoại lệ nào xảy ra, ngay cả khi khối `except` có thể đưa chương trình quay lại luồng xử lý chính.

Trong Python, khối `try/except` còn được dùng phổ biến trong kiểm soát luồng (tương tự như khối `if/else`), chứ không chỉ là xử lý lỗi. Điều này xuất phát từ triểt lý lập trình của Python là *Easier to ask for forgiveness than permission* (EAFP), đối lập với triết lý *Look before you leap* (LBYL) trong các ngôn ngữ khác như C:
-   EAFP: Giả định trước rằng thông tin nào đó là hợp lệ và truy cập nó ngay lập tức, nếu ngoại lệ xảy ra, thì sẽ bắt và xử lý nó sau. Đặc trưng của phong cách này là code chứa rất nhiều khối `try/except`
-   LBYL: Kiểm tra điều kiện trước khi truy cập thông tin nào đó. Đặc trưng của phong cách này là trong code chứa nhiều khối `if/else`

Trong môi trường đa luồng, LBYL đem đến rủi ro xảy ra race condition do khoảng delay giữa bước kiểm tra và bước thực thi. Ví dụ, luồng A kiểm tra thấy khóa `k` nằm trong dict `d`, nhưng trước khi truy xuất `d[k]`, một luồng khác tiến hành xóa `k` khỏi `d`, khi đó A truy cập `k` sẽ sinh ra lỗi. Vấn đề này có thể xử lý thông qua lock hoặc dùng phong cách `EAFP`: cứ truy vấn luôn `d[k]`, nếu xảy ra ngoại lệ `KeyError` (do `k` không có từ trước, hay do luồng khác xóa đi) thì sẽ trả về `None`.

---
### Context Managers and with Blocks

Context manager objects được tạo ra để phục vụ mệnh đề `with`, giống như cách iterators phục vụ mệnh đề `for`.

Context management sơ khai được thực hiện bởi khối `try...finally`.
-   Khối `try`:
    -    "set up context" (mở file, kết nối cơ sở dữ liệu, ...)
    -    "do something in the context".
-   Khối `finally`: 
    -   "tear down context" (đóng file, đóng kết nối csdl, ...)
    -   Luôn được thực hiện, ngay cả khi luồng xử lý bị ngắt bởi ngoại lệ, bởi lệnh `return` hay cú pháp `sys.exit()`.

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
-   Quá trình tạo và hủy context được đóng gói trong hai phương thức `__enter__` và `__exit__` của lớp `Ctx`, lớp này chính là một context manager
-   `obj` có thể không phải là thể hiện của `Ctx`, nó là đối tượng trả về của phương thức `Ctx.__enter__()`. Ví dụ như khi mở file, ta cần nhận về một đối tượng file để thao tác trên nó, nhưng trong hầu hết các trường hợp khác, ta không cần lấy về đối tượng này

Và khối `try...finally` trên tương đương với một khối `with` đơn giản hơn rất nhiều:

```python
with Ctx() as obj:
    do_something()
```

Như vậy, quá trình thiết kế và sử dụng context manager thông qua hai bước:
1.  Thiết kế context manager: Một lớp implement context manager protocol với hai phương thức `__enter__` và `__exit__`
2.  Sử dụng context manager với câu lệnh `with`

Ví dụ: Ta sẽ implement một context manager khá thú vị: bên trong context, hàm `print` sẽ in ra màn hình xâu đầu vào nhưng bị đảo ngược lại, kết thúc context, hàm `print` lại in ra xâu như bình thường.

Mã nguồn của context manager này như sau:
```python
class LookingGlass:
    def __enter__(self):
        import sys
        self.original_write = sys.stdout.write
        sys.stdout.write = self.reverse_write
    
    def reverse_write(self, text):
        self.original_write(text[::-1])
    
    def __exit__(self, exc_type, exc_value, traceback):
        import sys
        sys.stdout.write = self.original_write
```

Kết quả:
```python
>>> with LookingGlass() as what:
...     print('Alice, Kitty and Snowdrop')
...
pordwonS dna yttiK ,ecilA
>>> print('Back to normal')
Back to normal
```

---
### The contextlib Module

Module `contextlib` cung cấp nhiều context manager mặc định hay ho:

-   Tạm thời chuyển luồng ra chuẩn thành file `f`:
    ```python
    with contextlib.redirect_stdout(f):
        do_something()
    ```

-   Nếu đối tượng nào đó có phương thức `close()`, ngụ ý rằng nên "đóng" nó lại khi không dùng đến nữa => Tự động đóng nó bằng context manager `closing`:
    ```python
    with contextlib.closing(closable_obj):
        do_something()
    ```

-   Bỏ qua một vài ngoại lệ nào đó trong một xử lý:
    ```python
    with contextlib.suppress(*exceptions):
        do_something()
    ```

-   Tự tạo một context manager từ một generator function:
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
    Chú ý:
    -   Giá trị được `yield` ra là giá trị nhận về sau từ khóa `as` trong cấu trúc `with...as`
    -   `acquire_resource` là thao tác set up context
    -   `release_resource` là thao tác tear down context

---
### Using @contextmanager

Ta có thể implement lại lớp `LookingGlass` sử dụng `@contextmanager` như sau:

```python
import contextlib

@contextlib.contextmanager
def looking_glass():
    # __enter__
    import sys
    original_write = sys.stdout.write

    def reverse_write(text):
        original_write(text[::-1])
    
    sys.stdout.write = reverse_write
    
    # halt
    try:
        yield
    finally:
        # __exit__
        sys.stdout.write = original_write
```

*Chú ý:*
-   Nếu đoạn code trong khối `with` gây ra exception, exception đó sẽ bị raise lại tại chỗ `yield`. Do vậy ta cần đặt `yield` trong khối `try/finally` để đảm bảo hành động cập nhật lại `sys.stdout.write` luôn được thực hiện

---
### Summary

> TBD

---
### Soapbox

> TBD