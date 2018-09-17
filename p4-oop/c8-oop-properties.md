# Object References, Mutability and Recycling

## Variable Are Not Boxes

Biến lưu trữ tham chiếu đến đối tượng chứ không lưu trữ bản sao của đối tượng. Hãy tưởng tượng các biến là các nhãn gắn lên đối tượng chứ không phải là các hộp để lưu trữ đối tượng.

## Identity, Equality and Aliases

Tham chiếu từ biến đến đối tượng được thực hiện bằng phép gán biến cho đối tượng, khi ta gán biến cho đối tượng mới, ta tham chiếu biến đến đối tượng mới.

Để thay đổi đối tượng, ta phải thực hiện qua biến tham chiếu tới nó. Ví dụ:

```python
x = [1, 2, 3]
x.append(4) # append 4 to the list referenced by x
```

Một đối tượng được hai biến x và y tham chiếu đến, nếu thay đổi đối tượng bằng biến x, tham chiếu từ y cũng thay đổi theo:

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

### Equal or Is

Phép so sánh `==` so sánh giá trị của hai đối tượng.

Phép kiểm tra `is` kiểm tra xem hai biến có tham chiếu đến cùng một đối tượng hay không.

Ngoại lệ khi so sánh với singleton, `is` được chuộng dùng hơn `==` vì nó nhanh hơn (`==` có thể bị overload, dẫn tới thời gian xử lý lâu hơn)

```python
x is None
x is not None
```

### The Relative Immutability of Tuples

Tuples, giống như bất kỳ Python collections nào, lưu trữ tham chiếu đến các đối tượng mà nó chứa. Nếu các thành phần của một tuple là mutable, nó có thể được thay đổi, mặc dù bản thân tuple là immutable. Nói cách khác, tuple chỉ immutable đối với các tham chiếu mà nó lưu trữ, không immutable với dữ liệu mà nó tham chiếu đến.

----

Sự khác biệt giữa hai khái niệm 'bằng nhau' và 'đồng nhất' ảnh hưởng đến một thao tác khác: copy một object. Khi ta copy object, ta tạo ra một object mới 'bằng' object cũ nhưng không 'đồng nhất' với object cũ (khác id). Nhưng nếu object được copy ra chứa các objects khác, liệu các objects bên trong có nên được copy không, hay ta có thể dùng chung chúng? Không có câu trả lời nào cụ thể cả, hãy đọc tiếp để tìm hiểu thêm!

## Shallow Copy vs Deep Copy

Hai cách đơn giản nhất để copy một sequence là:

*   Dùng built-in constructor của kiểu tương ứng:

    ```python
    >>> l1 = [1, 2, 3]
    >>> l2 = list(l1)
    >>> l2
    [1, 2, 3]
    >>> l2 is l1
    False
    ```

*   Dùng cú pháp slicing: **`l2 = l1[:]`**

Tuy nhiên, theo mặc định hai cách này chỉ thực hiện shallow copy, tức là chỉ container được tạo mới, các phần tử trong sequence chỉ là các reference đến các phần tử cũ. Nếu các phần tử của sequence là immutable, cách làm này không gây hại gì, nhưng nếu ngược lại, đôi khi nó gây ra những tác dụng phụ không đáng có.

Ngược lại, deep copy giúp tạo bản sao của một đối tượng và các phần tử của nó một cách đệ quy, giúp tạo ra một đối tượng hoàn toàn mới không dính dáng gì đến đối tượng ban đầu. Cách làm này tốn kém thời gian và chi phí, chỉ nên được thực hiện khi bắt buộc.

### Deep and Shallow Copy of Arbitrary Objects

Module **`copy`** cung cấp hàm **`deepcopy()`** và **`copy()`** để thực hiện deep copy hoặc shallow copy một đối tượng bất kỳ.

Deep copy không được sử dụng cho object tham chiếu đến các tài nguyên bên ngoài hoặc chứa các singleton. Có thể implement phương thức **`__deepcopy__()`** để chỉ định cụ thể cách thức xử lý đối với những trường hợp đặc biệt như thế này.

## Function Parameters as References

Chế độ truyền tham số vào hàm duy nhất hỗ trợ bởi Python cũng như hầu hết các ngôn ngữ lập trình hướng đối tượng khác là chế độ *call by sharing*, có nghĩa là tạo ra các aliases tham chiếu đến các tham số truyền vào hàm và sử dụng các aliases này trong phần thân hàm.

Hệ quả của cơ chế này đó là một hàm có thể thay thế hoàn toàn một object được truyền vào nó bởi một object khác. Ví dụ dưới đây giải thích kĩ hơn về vấn đề này

*   Giả sử ta có 2 tuple **`a`** và **`b`**:
    ```python
    >>> a = (1, 2); b = (3, 4)
    >>> id(a)
    140445269766512
    ```
*   Thực hiện phép toán **`a += b`**, tức là gán tuple **`a`** bằng tuple **`a + b`**, như dự đoán, id của a đã thay đổi:
    ```python
    >>> a += b
    >>> id(a)
    140445270056728
    ```
*   Bây giờ ta implement cú pháp này trong một hàm:
    ```python
    def f(a, b):
        a += b
        return a
    ```
*   Gọi hàm **`f`** với tham số **`a`** và **`b`**:
    ```python
    >>> a = (1, 2); b = (3, 4)
    >>> f(a, b)
    (1, 2, 3, 4)
    >>> a
    (1, 2)
    ```
Như vậy có thể thấy biến **`a`** không thể bị thay thế bởi hàm. Thực hiện tương tự với **`a`** là một list, ta thấy tuy nó thay đổi về giá trị nhưng cũng không thay đổi id.

### Mutable Types As Parameter Defaults: bad idea

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

### Defensive Programming with Mutable Parameters

Khi tạo ra một hàm nhận vào một tham số mutable, hãy cẩn thận suy xét đến trường hợp người dùng có thể thay đổi tham số đó hay không, và bởi vậy hãy có những biện pháp phòng ngừa những sự thay đổi đó.

*   Nếu việc thay đổi tham số không có tác động gì đáng kể, có thể truyền nó vào hàm như bình thường:

    ```python
    ...
    def __init__(self, name):
        self.name = name
    ...
    ```
*   Tuy nhiên, nếu như việc thay đổi tham số có thể dẫn đến những tác động không mong muốn, hãy nhớ copy tham số đó ra trước khi sử dụng:

    ```python
    import copy

    def do_something(self, mutable_obj):
        self.obj = copy.copy(mutable_obj)

    def do_otherthing(self, stuff=None):
        if stuff is None:
            self.stuff = []
        else:
            self.stuff = list(stuff)
    ``` 

*Việc gán object cho instance variable được thực hiện theo một trong các cách sau với độ ưu tiên giảm dần:*

1.  **Ưu tiên hàng đầu**: Sử dụng immutable instance variables
2.  **Phòng ngừa**: Copy object trước khi gán nó cho instance variables
3.  **Không phòng ngừa**: Chắc chắn rằng việc thay đổi object không để lại tác dụng phụ nào trước khi gán chúng một cách trực tiếp
4.  **Không được phép**: Gán mutable instance variables một cách tùy tiện

## Gargage Collection

Lệnh **`del`** chỉ xóa bỏ tham chiếu đến object, không phải bản thân object đó. Nếu tham chiếu được xóa bỏ là link cuối cùng đến object, chỉ khi đó object mới bị hủy hoàn toàn.

Có nhiều gabage collector được implement bởi Python nhằm tự động giải phóng vùng nhớ chiếm bởi các đối tượng không còn được tham chiếu đến nữa. Thao tác thường được sử dụng đó là implement và sử dụng phương thức **`__del__()`** cho đối tượng `obj` khi gọi lệnh `del(obj)`.

### Weak References

Weak references tới đối tượng giống hệt như symbolic links tới files trong Linux với hai đặc điểm chính:

*   Xóa bỏ một weak reference không ảnh hưởng gì tới đối tượng mà nó trỏ tới
*   Nếu đối tượng chỉ còn được trỏ tới bởi các weak references, nó sẽ bị hủy và các weak references sẽ trỏ tới **`None`**

Một usecase thường dùng là cơ chế caching, các items được lưu trữ tạm trong một bản ghi cache kiểu `dict`, khi các "hard" references tới một item bị gỡ bỏ, item cũng sẽ bị loại bỏ ra khỏi cache luôn.

#### weakref Module

Module **`weakref`** cung cấp các class thao tác với weak references:

*   **`weakref.ref(obj)`**: tạo weak reference tới `obj` 
*   **`weakref.finalize(obj, finalizer)`**: Chạy hàm `finalizer` khi `obj` bị dọn dẹp khỏi bộ nhớ
*   **`weakref.WeakValueDictionary`**: Tạo các weak references tới các obj và đóng chúng trong một kiểu `dict`. ***Nó có thể được dùng để gắn thêm thông tin cho một đối tượng mà không cần phải thêm thuộc tính cho nó***
*   **`weakref.WeakSet`**: Lưu trữ các weak references trong một set. Nếu bạn cần xây dựng một lớp có khả năng kiểm soát được tất cả các thể hiện của nó, `WeakSet` là một lựa chọn tốt. Ngược lại, nếu chỉ dùng `set` thông thường, các thể hiện của lớp sẽ không bao giờ được giải phóng cho đến khi tiến trình kết thúc.

#### Limintations of Weak References

Không phải tất cả các đối tượng trong Python đều hỗ trợ weak referece, đặc biệt là các kiểu built-in

*   Có thể weak reference trực tiếp đến **`set`**
*   Có thể weak reference đến subclass của **`dict`** và **`list`**
*   Không thể weak reference đến subclass của **`int`** hat **`tuple`**

Lý do là bởi cơ chế cài đặt CPython bên dưới của các kiểu này sử dụng các phương thức tối ưu khác nhau.

## Summary

*   Mỗi biến tạo một tham chiếu đến một đối tượng, một đối tượng có thể được tham chiếu tới bởi nhiều biến, khi nó không còn được tham chiếu nữa, nó sẽ được giải phóng bởi Python garbage collector. Dùng lệnh **`del`** nhằm loại bỏ một ham chiếu đến một đối tượng

*   Tuple là immutable, nhưng các phần tử của nó có thể là các mutable objects

*   Khác với các khái niệm "call by value" (truyền tham trị) và "call by reference" (truyền tham chiếu) tồn tại trong các ngôn ngữ lập trình khác, Python sử dụng khái niệm "call by sharing". Điều này có nghĩa là, khi truyền một biến vào hàm như một tham số, sẽ có một tham chiếu khác được tạo ra tới đối tượng mà biến này tham chiếu đến, và mỗi lần sử dụng biến này trong hàm, ta sử dụng tham chiếu được sao ra chứ không phải tham chiếu ban đầu. Điều này khiến ta chỉ có thể thay đổi giá trị của đối tượng (nếu đối tượng là immutable) mà không thể thay đổi định danh của biến bên ngoài phạm vi của hàm.

*   Shallow copy một đối tượng chỉ tạo ra cái "vỏ" mới, các thuộc tính của đối tượng được copy ra chỉ là các tham chiếu khác đến vùng nhớ mà các thuộc tính tương ứng của đối tượng ban đầu trỏ đến. Ngược lại, deep copy là khởi tạo lại đối tượng, kể cả các thành phần của nó chứa (việc làm này là tốn kém tài nguyên, hãy cân nhắc sử dụng chỉ khi thực sự cần thiết). Module **`copy`** giúp shallow và deep copy một cách hiệu quả

*   Đối với các immutable object không chứa các mutable object (**`frozenset`**, **`int`**, **`str`**, ...), thao tác shallow copy chỉ đơn giản là tạo reference đến đối tượng cũ. Mặc dù đây là một sự dối trá, nhưng nó tiết kiệm và hoàn toàn không có sự khác biệt nào dưới con mắt người dùng

*   Không được phép truyền một mutable object vào tham số mặc định cho hàm, bởi tất cả các đối tượng được tạo ra theo tham số mặc định chia sẻ chung tham chiếu tới nó, sự thay đổi tham số mặc định ở một đối tượng sẽ ảnh hưởng tới các đối tượng khác

*   Không gán thuộc tính bằng một mutable object nếu không chắc chắn rằng việc làm này không gây ảnh hưởng gì. Để đảm bảo an toàn, hãy copy đối tượng ra trước khi gán

*   Sử dụng hard reference tới một đối tượng (bằng cách gán nó cho một biến) có thể ngăn chặn nó khỏi việc bị Python garbage collector dọn dẹp, ngay cả khi ta không còn thực sự sử dụng nó nữa. Sử dụng weak reference với module **`weakref`** giúp tham chiếu tới một đối tượng chỉ khi nó còn hữu dụng

## Pythonic Programming Tricks

*   Các biến tạm được sinh ra trong cấu trúc lặp `for...in` được giữ lại bên ngoài phạm vi của nó (ví dụ biến count), đây là tính năng hữu dụng vì các biến này lưu giữ giá trị được gán ở vòng lặp cuối cùng, có thể được tận dụng để sử dụng ở bên ngoài vòng lặp
