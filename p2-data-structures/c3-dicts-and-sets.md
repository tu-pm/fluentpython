## Chapter 3: Dictionaries and Sets

---
###   Table of Contents
- [Chapter 3: Dictionaries and Sets](#chapter-3-dictionaries-and-sets)
  - [Table of Contents](#table-of-contents)
  - [Generic Mapping Types](#generic-mapping-types)
  - [dict Comprehensions](#dict-comprehensions)
  - [Overview of Common Mapping Methods](#overview-of-common-mapping-methods)
  - [Mappings with Flexible Key Lookup](#mappings-with-flexible-key-lookup)
  - [Variations of dict](#variations-of-dict)
  - [Subclassing UserDict](#subclassing-userdict)
  - [Immutable Mappings](#immutable-mappings)
  - [Set Theory](#set-theory)
  - [dict and set Under the Hood](#dict-and-set-under-the-hood)
  - [Summary](#summary)

---
###  Generic Mapping Types

Điều kiện để một Python object là hashable là:
1.  Đối tượng đó phải so sánh được với đối tượng khác thông qua phép so sánh `==` (implement phương thức `__eq__`)
2.  Đối tượng implement phương thức `__hash__`
3.  Đối tượng là immutable (điều kiện lỏng)
4.  Nếu nó là container, các items bên trong nó phải là hashable

Ví dụ:
-   `list` là unhashable:
    ```python
    >>> hash([1, 2])
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: unhashable type: 'list'
    ```
-   `tuple` chứa các phần tử kiểu `int` là hashable
    ```python
    >>> hash((1, 2))
    -3550055125485641917
    ```
-   Nhưng `tuple` chứa `list` thì lại không hashable, do hàm `hash` của tuple gọi `hash` trên các items của nó:
    ```python
    >>> hash(([1,2],))
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: unhashable type: 'list'
    ```

Theo mặc định, mọi đối tượng do người dùng tự định nghĩa đều là hashable, do `hash()` sẽ trả về `id` của đối tượng và `==` cũng so sánh `id` nếu hàm `__eq__` không được định nghĩa. Ngược lại, lập trình viên cần đảm bảo ba điều kiện trên được thỏa mãn nếu muốn custom object của mình là hashable.

---
###  dict Comprehensions

---
###  Overview of Common Mapping Methods

---
###  Mappings with Flexible Key Lookup

---
###  Variations of dict

---
###  Subclassing UserDict

---
###  Immutable Mappings

---
###  Set Theory

---
###  dict and set Under the Hood

---
###  Summary