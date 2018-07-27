# FluentPython-P3-C7: Function Decorators and Closures

The end goal of this chapter is to explain exactly how function decorators work, from the simplest registration decorators to the rather more complicated parametrized ones.

However, before we reach that goal we need to cover:

*   How Python evaluates decorator syntax
*   How Python decides whether a variable is local
*   Why closures exist and how they work
*   What problem is solved by nonlocal

With this grounding we can tackle further decorator topics:

*   Implementing a well-behaved decorator
*   Interesting decorators in the standard library
*   Implementing a parametrized decorator

## Decorators 101

Một decorator là một callable mà lấy tham số truyền vào là một hàm khác (hàm này gọi là decorated function). Decorator thực hiện một vài thao tác xử lý trên decorated function và trả về hàm này hoặc thay thế nó bởi một callable khác

Nói cách khác, đoạn code này:

```python
@decorate
def target():
    print('running target()')
```

Có tác dụng tương tự như:

```python
def target():
    print('running target()')

target = decorate(target)
```

Hai điểm cần lưu ý đối với decorators:

*   decorated functions sẽ bị thay thế bởi hàm mà decorator trả về
*   Thao tác thay thế decorated function được thực hiện ngay khi module được load, chứ không phải đến khi decorated function được gọi

## When Python Executes Decorators

Như đã nói, decorators được thực thi ngay khi module được import (ví dụ trang 185-186). Mặt khác, decorated functions chỉ chạy khi nó được gọi một cách trực tiếp. Đây chính là điểm khác biệt giữa *import time* và *run time*.

Thông thường, decorators được định nghĩa trong một module và có thể được sử dụng cho hàm ở module khác. Bên cạnh đó, hầu hết các decorator định nghĩa ra một inner function và trả về nó, thay vì trả về hàm ban đầu (decorated function).

***Trick:***

*   Cú pháp `'%s' % obj` có chức năng format `obj` về dạng xâu bằng cách gọi đến phương thức `__repr__` của nó

## Decorator Enhanced Strategy Pattern

Trong ví dụ tính discount ở chương 6 về strategy pattern, ta phải duy trì một danh sách các chiến lược promotion để sau đó hàm `best_promo` có thể đánh giá từng chiến lược trong danh sách này và đưa ra kết quả tốt nhất. Vấn đề nảy sinh nếu hard-code danh sách này đó là mỗi khi có người thêm một chiến lược discount mới, họ lại phải thêm nó vào danh sách một cách thủ công. Decorator giúp giải quyết vấn đề này một cách gọn gàng và đẹp mắt:

*   Bước 1: Định nghĩa decorator `promotion` có chức năng tự động thêm các chiến lược vào `promos` list:
    ```python
    promos = []
    
    def promotion(promo_func):
        promos.append(promo_func)
        return promo_func
    ```

*   Bước 2: Với mỗi chiến lược discount, ta thêm decorator `@promotion` phía trước, như vậy chúng sẽ được thêm vào `promos` mà không lo bị sót
    ```python
    @promotion
    def fidelity(order):
        ...
    
    @promotion
    def bulk_item(order):
        ...

    @promotion
    def large_order(order):
        ...
    ```

Việc làm này đem lại nhiều tác dụng:

*   Không cần quy tắc tên đặc biệt cho các hàm để chương trình có thể phân loại các hàm
*   Làm nổi bật chức năng của hàm, tăng tính khả đọc
*   Dễ dàng disable một promotion nào đó bằng việc comment decorator
*   Có thể định nghĩa chiến lược discount từ module khác, miễn là chúng sử dụng decorator `@promotion`

Như đã nói, decorator hầu như đều thay thế decorated function bằng một inner function khai báo bên trong nó. Để thực hiện được điều này, cần nắm vững về closures mà trước hết là phạm vi biến trong Python.

## Variable Scope Rules

*   Rule #1: Khi một biến được khai báo trong phạm vi của một hàm, nó mặc định là biến cục bộ. Trong trường hợp ta đã khai báo biến này bên ngoài hàm và reference đến nó bên trong hàm trước khi nó được định nghĩa lại là biến cục bộ, chương trình vẫn sẽ không chạy.

*   Rule #2: Sử dụng từ khóa `global` để khai báo biến toàn cục bên trong hàm

## Closures


