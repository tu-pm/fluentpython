## Chapter 8: Object References, Mutability and Recycling

---
### Table of Contents
- [Chapter 8: Object References, Mutability and Recycling](#chapter-8-object-references-mutability-and-recycling)
  - [Table of Contents](#table-of-contents)
  - [Variable Are Not Boxes](#variable-are-not-boxes)
  - [Identity, Equality and Aliases](#identity-equality-and-aliases)
  - [Shallow Copy vs Deep Copy](#shallow-copy-vs-deep-copy)
    - [Shallow Copy](#shallow-copy)
    - [Deep Copy](#deep-copy)
  - [Function Parameters as References](#function-parameters-as-references)
    - [Mutable Types As Parameter Defaults: bad idea](#mutable-types-as-parameter-defaults-bad-idea)
    - [Defensive Programming with Mutable Parameters](#defensive-programming-with-mutable-parameters)
  - [Garbage Collection](#garbage-collection)
  - [Weak References](#weak-references)
  - [Fun facts](#fun-facts)
  - [Summary](#summary)

---
### Variable Are Not Boxes

Biến là cái nhãn gắn lên đối tượng chứ không phải là cái hộp để lưu trữ đối tượng.

---
### Identity, Equality and Aliases

Tham chiếu được tạo ra bằng phép gán biến cho đối tượng. Việc cập nhật đối tượng được thực hiện qua biến tham chiếu tới nó. Ví dụ:

```python
x = [1, 2, 3]
x.append(4) # append 4 to the list referenced by x
```

Nếu một đối tượng được hai biến x và y tham chiếu đến, khi cập nhật đối tượng bằng biến x, tham chiếu từ y cũng thay đổi theo:

```python
>>> charles = {'name': 'Charles L. Dodgson', 'born': 1832}
>>> lewis = charles
>>> lewis is charles
True
>>> id(charles), id(lewis)
(4300473992, 4300473992)
>>> lewis['balance'] = 950
>>> charles
{'name': 'Charles L. Dodgson', 'balance': 950, 'born': 1832}
```

Việc thực hiện nhiều tham chiếu tới cùng một đối tượng gọi là *aliasing*.

Phân biệt giữa hai khái niệm bằng nhau (equal) và đồng nhất (is): 
-   Phép so sánh `==` so sánh giá trị của hai đối tượng có bằng nhau không
-   Phép kiểm tra `is` kiểm tra xem hai biến có tham chiếu đến cùng một đối tượng hay không.
-   Khi so sánh với singleton, `is` được chuộng dùng hơn `==` vì nó nhanh hơn (`==` có thể bị overload, dẫn tới thời gian xử lý lâu hơn):
    ```python
    x is None
    x is not None
    ```

Tuples, giống như bất kỳ Python collections nào, lưu trữ tham chiếu đến các đối tượng mà nó chứa. Nếu các thành phần của một tuple là mutable, chúng có thể được thay đổi, cho dù bản thân tuple là immutable. Nói cách khác, tuple chỉ immutable đối với các tham chiếu mà nó lưu trữ, không immutable với dữ liệu mà nó tham chiếu đến.

Sự khác biệt giữa hai khái niệm *bằng nhau* và *đồng nhất* ảnh hưởng đến một thao tác khác: copy một object, sẽ được bàn đến ở phần sau.

---
### Shallow Copy vs Deep Copy

#### Shallow Copy

Khi ta copy object, ta tạo ra một object mới *bằng* object cũ nhưng không *đồng nhất* với object cũ (khác id). Nhưng nếu object đó chứa các objects khác, liệu các objects bên trong có nên được copy không, hay ta có thể dùng chung chúng?

Nếu ta chỉ copy object bên ngoài (container), đó gọi là *shallow copy*, đây cũng là hành vi copy mặc định khi copy containers trong Python. Hai cách đơn giản nhất để copy một sequence là:
-   Dùng built-in constructor của kiểu tương ứng:
    ```python
    >>> l1 = [1, 2, 3]
    >>> l2 = list(l1)
    >>> l2
    [1, 2, 3]
    >>> l2 is l1
    False
    ```
-   Dùng cú pháp slicing: 
    ```python
    >>> l2 = l1[:]
    >>> l2 is l1
    False
    ```

*Lưu ý khi sử dụng shallow copy:*
-   Nếu các phần tử của sequence là immutable, shallow copy không gây hại gì. Nhưng nếu ngược lại, việc thay đổi phần tử của sequence được copy ra sẽ làm thay đổi phần tử tương ứng trên sequence gốc, vì bản chất chúng là một

#### Deep Copy

Trường hợp thứ hai, ta cần tạo bản sao của một đối tượng và các phần tử của nó một cách đệ quy, giúp tạo ra một đối tượng hoàn toàn mới không dính dáng gì đến đối tượng ban đầu. Cách làm này gọi là *deep copy* và được thực hiện bằng cú pháp `copy.deepcopy(obj)`:
```python
>>> a = [1, 2]
>>> b = [a, 3]
>>> b
[[1, 2], 3]
>>> from copy import deepcopy
>>> c = deepcopy(b)
>>> a.append(4)
>>> b
[[1, 2, 4], 3]
>>> c
[[1, 2], 3]
```

*Lưu ý khi sử dụng deep copy:*
-   Việc copy đối tượng một cách đệ quy là tốn kém và chỉ nên dùng khi thực sự cần thiết
-   Đối tượng có thể có tham chiếu vòng, điều này có thể gây lặp vô hạn nếu không xử lý chính xác (`deepcopy` xử lý bằng cách lưu lại các đối tượng đã copy rồi và không copy lại)
-   Các phần tử là external resources hay singletons là không được phép copy, ta cần implement phương thức `__deepcopy__` trên đối tượng một cách chính xác để giúp hàm `deepcopy` xử lý được các trường hợp này

---
### Function Parameters as References

Phương thức truyền tham số vào hàm duy nhất hỗ trợ bởi Python là *call by sharing*. Tức là tạo ra các aliases tham chiếu đến các đối tượng truyền vào hàm và sử dụng các aliases này trong phần thân hàm.

Hệ quả của cơ chế này đó là ta có thể gán tham số trong chữ ký hàm vào một object khác. Ví dụ dưới đây giải thích kĩ hơn về vấn đề này

-   Giả sử ta có 2 tuple `a` và `b`:
    ```python
    >>> a = (1, 2); b = (3, 4)
    >>> id(a)
    140445269766512
    ```
-   Thực hiện phép toán `a += b`, tức là gán tuple `a` bằng tuple `a + b`, như dự đoán, id của a đã thay đổi:
    ```python
    >>> a += b
    >>> id(a)
    140445270056728
    ```
-   Bây giờ ta implement cú pháp này trong một hàm:
    ```python
    def f(a, b):
        a += b
        return a
    ```
-   Gọi hàm `f` với tham số `a` và `b`:
    ```python
    >>> a = (1, 2); b = (3, 4)
    >>> f(a, b)
    (1, 2, 3, 4)
    >>> a
    (1, 2)
    ```
Như vậy có thể thấy biến `a` không thể bị thay thế bởi hàm. Thực hiện tương tự với `a` là một list, ta thấy tuy nó thay đổi về giá trị nhưng cũng không thay đổi id. *Tham số của hàm bản chất chỉ là  một alias trỏ tới đối tượng truyền vào tham số đó*.

#### Mutable Types As Parameter Defaults: bad idea

Không nên sử dụng mutable object làm tham số mặc định cho hàm, bởi vì tham số mặc định là *chia sẻ chung*, các đối tượng sử dụng tham số mặc định sẽ cùng tham chiếu đến nó và vì thế có thể cùng thay đổi nó nếu nó là mutable:

```python
>>> class Dummy(object):
...         def __init__(self, default_arg='xxx')
                self.default_arg = default_arg
>>> dummy1 = Dummy()
>>> dummy2 = Dummy()
>>> dummy1.__init__.__defaults__[0] is dummy2.__init__.__defaults__[0]
True
```

#### Defensive Programming with Mutable Parameters

Khi viết hàm nhận vào một tham số mutable, hãy cẩn thận suy xét đến trường hợp người dùng có thể thay đổi tham số đó hay không, và hãy có những biện pháp phòng ngừa cho những sự thay đổi đó.

-   Nếu việc thay đổi tham số không có tác động gì đáng kể, có thể truyền nó vào hàm như bình thường:
    ```python
    def __init__(self, name):
        self.name = name
    ```
-   Tuy nhiên, nếu như việc thay đổi tham số có thể dẫn đến những tác động không mong muốn, hãy nhớ copy tham số đó ra trước khi sử dụng:
    ```python
    import copy

    # Copy a mutable object
    def do_something(self, mutable_obj):
        self.obj = copy.copy(mutable_obj)

    # Copy a (mutable) list
    def do_otherthing(self, stuff=None):
        if stuff is None:
            self.stuff = []
        else:
            self.stuff = list(stuff)
    ``` 

Hãy sử dụng các chiến lược lập trình phòng ngừa đối với muable objects sau với độ ưu tiên giảm dần:
1.  *Ưu tiên hàng đầu*: Sử dụng immutable instance variables
2.  *Phòng ngừa*: Copy object trước khi gán nó cho instance variables
3.  *Không phòng ngừa*: Chắc chắn rằng việc thay đổi object không để lại tác dụng phụ nào trước khi gán chúng một cách trực tiếp
4.  *Không được phép*: Gán mutable instance variables một cách tùy tiện

---
### Garbage Collection

Lệnh `del` chỉ xóa bỏ tham chiếu đến object, không phải bản thân object đó. Chỉ khi tham chiếu được xóa bỏ là link cuối cùng đến object thì object mới bị hủy hoàn toàn.

Bạn có thể implement và sử dụng phương thức `__del__()` cho đối tượng `obj` khi gọi lệnh `del(obj)` để chỉ định cách dọn dẹp đối tượng `obj` ra khỏi vùng nhớ khi không sử dụng đến nữa.

---
### Weak References

Weak references tới đối tượng giống như symbolic links tới files trong Linux ở hai đặc điểm chính:
-   Xóa bỏ một weak reference không ảnh hưởng gì tới đối tượng mà nó trỏ tới
-   Nếu đối tượng chỉ còn được trỏ tới bởi các weak references, nó sẽ bị hủy và các weak references sẽ trỏ tới `None`

Ví dụ sử dụng `weakref`:
```python
>>> import weakref
>>> a = {0, 1}
>>> wref = weakref.ref(a)
>>> print(wref())
{0, 1}
>>> a = {2, 3} # a now points to a different object
>>> print(wref())
None
```

Thường `weakref` được dùng để cache các đối tượng đã được tạo ra trong một `dict`, khi các "hard" references tới một item bị gỡ bỏ, item đó cũng sẽ bị loại bỏ ra khỏi cache luôn.

Module `weakref` cung cấp các function và class để thao tác với weak references:
-   `weakref.ref(obj)`: tạo weak reference tới `obj` 
-   `weakref.finalize(obj, finalizer)`: Chạy hàm `finalizer` khi `obj` bị dọn dẹp khỏi bộ nhớ
-   `weakref.WeakSet`: Lưu trữ các weak references trong một set. Nếu bạn cần xây dựng một class có khả năng kiểm soát được tất cả các instances của nó, `WeakSet` là một lựa chọn tốt. Vì nếu chỉ dùng `set` thông thường, các instances của lớp sẽ không bao giờ được giải phóng cho đến khi tiến trình kết thúc.
-   `weakref.WeakKeyDictionary` và `weakref.WeakValueDictionary`: Tương tự như `WeakSet`, nhưng các tham chiếu yếu là key hoặc value của một dict

**Nhược điểm của `weakref`**

Không phải tất cả các đối tượng trong Python đều hỗ trợ weak reference, đặc biệt là các kiểu built-in:
-   Có thể weak reference trực tiếp đến `set`
-   Có thể weak reference đến subclass của `dict` và `list`
-   Không thể weak reference đến subclass của `int` hat `tuple`

Lý do là bởi cơ chế cài đặt CPython bên dưới của các kiểu này sử dụng các phương thức tối ưu khác nhau.

### Fun facts

-   Các biến tạm được sinh ra trong cấu trúc lặp `for...in` được giữ lại bên ngoài phạm vi của nó (ví dụ biến count), đây là tính năng hữu dụng vì các biến này lưu giữ giá trị được gán ở vòng lặp cuối cùng, và có thể được tận dụng để sử dụng ở bên ngoài vòng lặp

-   Khi shallow copy các immutable types như `int`, `str`, `tuple` hay `frozenset`, kể cả bằng built-in constructor, bằng cú pháp slice hay bằng hàm `copy.copy()`, Python đều trả về một tham chiếu mới tới đối tượng cũ chứ không tạo ra đối tượng mới:
    ```python
    >>> t1 = (1, 2, 3) 
    >>> t2 = tuple(t1)
    >>> t2 is t1
    True
    ```

-   Khi khởi tạo các đối tượng built-in như `int` hay `str` cùng giá trị, CPython thường sử dụng lại các đối tượng đã được tạo trước đó, thay vì tạo ra đối tượng mới. Thủ thuật này được gọi là **interning** và thường xuất hiện trong nhiều ngôn ngữ lập trình. Kiểu dữ liệu được intern, phạm vi intern và kích thước đối tượng được intern phụ thuộc vào chi tiết của từng phiên bản của ngôn ngữ lập trình:
    ```python
    # strings are interned
    >>> s1 = 'ABC'
    >>> s2 = 'ABC'
    >>> s2 is s1
    True

    # but tupples aren't
    >>> t1 = (1, 2, 3)
    >>> t2 = (1, 2, 3)
    >>> t2 is t1
    False
    ```

### Summary

-   Mỗi biến là một tham chiếu đến một đối tượng, một đối tượng có thể được tham chiếu tới bởi nhiều biến, khi đối tượng không còn được tham chiếu nữa, nó sẽ được giải phóng bởi Python garbage collector. Có thể dùng lệnh `del` nhằm loại bỏ một ham chiếu đến một đối tượng

-   Tuple là immutable, nhưng các phần tử của nó có thể là các mutable objects

-   Khác với các khái niệm "call by value" (truyền tham trị) và "call by reference" (truyền tham chiếu) tồn tại trong các ngôn ngữ lập trình khác, Python sử dụng khái niệm "call by sharing". Điều này có nghĩa là, khi truyền một biến vào hàm như một tham số, sẽ có một tham chiếu khác được tạo ra tới đối tượng mà biến này tham chiếu đến, và mỗi lần sử dụng biến này trong hàm, ta sử dụng tham chiếu được sao ra chứ không phải tham chiếu ban đầu. Điều này khiến ta chỉ có thể thay đổi giá trị của đối tượng (nếu đối tượng là mutable) mà không thể thay đổi định danh của biến bên ngoài phạm vi của hàm.

-   Shallow copy một đối tượng chỉ tạo ra cái "vỏ" mới, các thuộc tính của đối tượng được copy ra chỉ là các tham chiếu khác đến vùng nhớ mà các thuộc tính tương ứng của đối tượng ban đầu trỏ đến. Ngược lại, deep copy là khởi tạo lại đối tượng, kể cả các thành phần của nó chứa (việc làm này là tốn kém tài nguyên, hãy cân nhắc sử dụng chỉ khi thực sự cần thiết). Module `copy` giúp shallow và deep copy một cách hiệu quả

-   Đối với các immutable object không chứa các mutable object (`frozenset`, `int`, `str`, ...), thao tác shallow copy chỉ đơn giản là tạo reference đến đối tượng cũ. Mặc dù đây là một sự "dối trá", nhưng nó tiết kiệm và hoàn toàn không có sự khác biệt nào dưới con mắt người dùng

-   Không được phép truyền một mutable object vào tham số mặc định cho hàm, bởi tất cả các đối tượng được tạo ra theo tham số mặc định chia sẻ chung tham chiếu tới nó, sự thay đổi tham số mặc định ở một đối tượng sẽ ảnh hưởng tới các đối tượng khác

-   Không gán thuộc tính bằng một mutable object nếu không chắc chắn rằng việc làm này không gây ảnh hưởng gì. Để đảm bảo an toàn, hãy copy đối tượng ra trước khi gán

-   Sử dụng hard reference tới một đối tượng (bằng cách gán nó cho một biến) có thể ngăn chặn nó khỏi việc bị Python garbage collector dọn dẹp, ngay cả khi ta không còn thực sự sử dụng nó nữa. Sử dụng weak reference với module `weakref` giúp tham chiếu tới một đối tượng chỉ khi nó còn hữu dụng