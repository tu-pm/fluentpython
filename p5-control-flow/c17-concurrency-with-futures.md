## Chapter 17: Concurrency with Future

> Phần lớn những người chê bai threads là những lập trình viên hệ thống thường xuyên làm việc với những ca sử dụng khù khoằm mà một lập trình viên ứng dụng thông thường chẳng bao giờ gặp phải. [..] Trong phần lớn trường hợp, khởi tạo và thực thi nhiều luồng độc lập rồi thu thập kết quả trong một hàng đợi là tất cả những gì mà một người lập trình ứng dụng cần biết về lập trình đồng thời (concurrent programming). - Michele Simionato

Chương này tập trung vào thư viện `cocurrent.futures` của Python - một thư viện có chức năng chính là đóng gói những công việc mà Michele Simionato đã nói đến ở trên thông qua một API đơn giản và dễ sử dụng.

Tôi cũng sẽ giới thiệu về khái niệm "futures" - các đối tượng đại diện cho sự thực thi bất đồng bộ của một hành động nào đó. Đây là một ý tưởng mạnh mẽ và là nền tảng của không chỉ `conccurent.futures` mà còn cả của `asyncio` - sẽ được bàn đến ở chương 18.

---
### Table of Contents

- [Chapter 17: Concurrency with Future](#chapter-17-concurrency-with-future)
  - [Table of Contents](#table-of-contents)
  - [Example: Web Downloads in Three Styles](#example-web-downloads-in-three-styles)
    - [A Sequential Download Script](#a-sequential-download-script)
    - [Downloading with concurrent.futures](#downloading-with-concurrentfutures)
    - [Where Are the Futures?](#where-are-the-futures)
  - [Blocking I/O and the GIL](#blocking-io-and-the-gil)
  - [Launching Processes with concurrent.futures](#launching-processes-with-concurrentfutures)
  - [Experimenting with Executor.map](#experimenting-with-executormap)
  - [Downloads with Progress Display and Error Handling](#downloads-with-progress-display-and-error-handling)
  - [Summary](#summary)

---
### Example: Web Downloads in Three Styles

Để xử lý network I/O một cách hiệu quả thì bạn phải biết đến concurrency. Lý do là bởi những thao tác với network đều có độ trễ lớn, thay vì lãng phí CPU cycles để ngồi đợi, sẽ tốt hơn nếu ta quay ra làm việc khác cho đến khi nhận được phản hồi từ phía bên kia kết nối network.

Để làm rõ quan điểm trên, tôi sẽ lấy ví dụ ba chương trình tải hình ảnh cờ của 20 quốc gia trên mạng về máy. Chương trình đầu tiên chạy một cách tuần tự: Nó chỉ tải ảnh tiếp theo nếu ảnh trước đó đã được lưu xuống ổ cứng. Hai chương trình còn lại tải ảnh một cách đồng thời và lưu xuống ổ cứng ngay khi chúng tải xong. Trong đó, một chương trình sử dụng `concurrent.futures` và một chương trình sử dụng `asyncio`.

Bạn có thể dễ dàng đoán được cách tải ảnh đồng thời sẽ nhanh hơn. Thực tế, hai cách tải ảnh đồng thời đều nhanh hơn cách tải tuần tự khoảng 5 lần, đối với các bài toán lớn hơn, hiệu quả của chúng còn lớn hơn thế.

Tại chương này, ta sẽ đi tìm hiểu mã nguồn của hai chương trình đầu tiên `flags.py` - chương trình tuần tự, và `flags_threadpool.py` - chương trình concurrent sử dụng `concurrent.futures`. Đoạn code cho chương trình `flags_asyncio.py` sẽ được trình bày ở chương 18.

Mục đích của ví dụ này là để làm rõ rằng, bất kể chiến lược lập trình đồng thời bạn sử dụng là gì - threads hay asyncio, nó đều làm chương trình của bạn trở nên nhanh hơn rất nhiều đối với các ứng dụng I/O bound, nếu được cài đặt một cách chính xác.

#### A Sequential Download Script

Đoạn code này không có gì quá thú vị, nhưng nó bao gồm những thủ tục cơ bản để tải ảnh quốc gia mà cũng sẽ được dùng trong các ví dụ sau, bao gồm lấy về mã quốc gia, tạo ra URL ảnh, download ảnh và lưu ảnh về ổ cứng.

Hàm `download_many()` thực hiện tải ảnh của 20 quốc gia cho trước một cách tuần tự và trả về số lượng ảnh đã tải.

```python
import os
import requests

POP20_CC = ('CN IN US ID BR PK NG BD RU JP '
            'MX PH VN ET EG DE IR TR CD FR').split()
BASE_URL = 'http://flupy.org/data/flags'
DEST_DIR = 'downloads/'

def save_flag(img, filename):
    path = os.path.join(DEST_DIR, filename)
    with open(path, 'wb') as fp:
    fp.write(img)

def get_flag(cc):
    url = '{}/{cc}/{cc}.gif'.format(BASE_URL, cc=cc.lower())
    resp = requests.get(url)
    return resp.content

def download_many(cc_list):
    for cc in sorted(cc_list):
        image = get_flag(cc)
        save_flag(image, cc.lower() + '.gif')
        return len(cc_list)
```

#### Downloading with concurrent.futures

Những tính năng chính của `concurrent.futures` package nằm trong hai class `ThreadPoolExecutor` và `ProcessPoolExecutor`. Chúng có tác dụng cung cấp một interface giúp bạn có thể truyền các callables vào và chạy chúng dưới nhiều luồng (threads) hoặc nhiều tiến trình (processes). Dưới đây là ví dụ tải ảnh đa luồng sử dụng `ThreadPoolExecutor`:

```python
from concurrent import futures

from flags import save_flag, get_flag, show, main

MAX_WORKERS = 20

def download_one(cc):
    image = get_flag(cc)
    save_flag(image, cc.lower() + '.gif')
    return cc 

def download_many(cc_list):
    workers = min(MAX_WORKERS, len(cc_list))
    with futures.ThreadPoolExecutor(workers) as executor:
      res = executor.map(download_one, cc_list)
    return len(list(res))
```

Chú ý:
-   Luôn chỉ ra số lượng workers tối đa khi lập trình đa luồng/đa tiến trình
-   `ThreadPoolExecutor` được khởi tạo với đầu vào là số lượng worker và trả về một đối tượng `executor`. Sau khi kết thúc context, phương thức `executor.shutdown(wait=True)` sẽ được gọi, khiến chương trình bị block cho đến khi toàn bộ các threads kết thúc.
-   Phương thức `executor.map` hoạt động tương tự như phương thức `map` built-in, điểm khác biệt là hành động `download_one` sẽ được thực thi cùng lúc trên tất cả item nằm trong `cc_list`

Ví dụ này tuy dễ hiểu, nhưng chưa làm rõ thế nào là *future*. Ta sẽ tìm hiểu rõ hơn ở mục tiếp theo.

#### Where Are the Futures?

Futures là thành phần quan trọng của cả `concurrent.futures` và `asyncio`, nhưng thường chúng không được nhìn thấy bởi người dùng. Mục này sẽ giới thiệu một cách tổng quan về chúng thông qua một ví dụ.

Kể từ Python 3.4, ta có hai class với cùng tên `Future` trong thư viện chuẩn: `concurrent.Future` và `asyncio.Futre`. Chúng có cùng ý nghĩa là đại diện cho một hành động nào đó được hoãn thực thi tại thời điểm hiện tại và có thể kết thúc hoặc không trong tương lai. `Future` trong hai thư viện này cũng giống như `Deferred` trong Twisted, `Future` trong Tornado và `Promise` trong Javascript.

Futures đóng gói các hành động đang chờ và đưa chúng vào hàng đợi, trạng thái của các hành động này có thể được theo dõi và kết quả hoặc ngoại lệ có thể được lấy về khi chúng thực hiện xong.

Người dùng không bao giờ tạo ra các đối tượng Futures một cách trực tiếp, chúng chỉ được tạo ra bởi framework khi người dùng lập lịch cho các tasks chạy đồng thời. Ví dụ, phương thức `Executor.submit()` nhận vào một callable, lập lịch cho nó được thực thi và trả về đối tượng future tương ứng.

Cả hai loại `Future` đều có phương thức `.done()`, báo rằng callable truyền vào `Future` đã được thực thi hay chưa. Nhưng thông thường, thay vì liên tục kiểm tra `.done()`, để thực thi hành động nào đó khi future thực hiện xong, người ta hay truyền callable thực thi hành động đó vào phương thức `.add_done_call_back()`. Khi đó, nếu future kết thúc thì callable này sẽ ngay lập tức được gọi (tương đồng với phương thức `Promise.then()` trong Javascript).

Cả hai cũng đều có một phương thức `.result()`, giúp trả về kết quả hoặc ngoại lệ của `Future` sau khi thực thi. Tuy nhiên, trong khi `Future` đang chờ thực thi, hành vi của phương thức này trên `concurrent.futures` và `asyncio` là rất khác nhau: `concurrent.futures` sẽ block luồng chính cho tới khi future kết thúc hoặc tới khi xảy ra timeout và tung ngoại lệ `TimeoutError`, trong khi `asyncio` thì không hỗ trợ timeout mà yêu cầu người dùng lấy về kết quả của future thông qua cú pháp `yield from`.

Nhiều phương thức khác của cả hai thư viện cũng có khả năng trả về các futures, số khác lại dùng futures để cài đặt thủ tục tính toán đồng thời một cách trong suốt với người dùng. Ví dụ, phương thức phương thức `.map()` ở trên trả về một iterable mà phương thức `__next__` trên nó trả về kết quả của các futures thay vì bản thân các đối tượng futures.

Ta có thể viết lại hàm `download_many` sử dụng cơ chế low-level hơn để hiểu thêm về cách hoạt động của futures:

```python
def download_many(cc_list):
    results = []
    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        todo = []
        for cc in cc_list:
            future = executor.submit(download_one, cc)
            todo.append(future)
        
        for future in futures.as_completed(todo):
            results.append(future.result())

    return len(results)
```

Chú ý:
-   Phương thức `.as_completed()` nhận vào tập hợp futures và yield ra các futures đã thực hiện xong
-   Các futures mà đã thực thi xong trong khoảng thời gian giữa hai lời gọi `.submit()` và `as_completed()` sẽ được trả về luôn trong vòng for
-   Tại một vòng lặp nào đó, nếu chờ quá lâu mà không có future nào thực hiện xong, ngoại lệ `TimeoutError` sẽ được tung ra

Chính xác mà nói, code của ta sử dụng `ThreadPoolExecutor` không hẳn là "đa luồng", do Python Global Interpreter Lock (GIL) chỉ cho phép một luồng chạy trong một thời điểm. Vậy tại sao đoạn code trên lại nhanh hơn nhiều so với code tuần tự? Hãy đọc tiếp để biết nguyên nhân tại sao GIL hầu như không hạn chế các tác vụ I/O thực thi bất đồng bộ.

---
### Blocking I/O and the GIL

Trình thông dịch CPython bản thân nó là không thread-safe, nên nó cần một Global Interpreter Lock (GIL) để chỉ cho phép một luồng thực thi Python bytecode tại một thời điểm. Đó là lý do tại sao một tiến trình Python thường không sử dụng được nhiều CPU core cùng lúc (điều này chỉ đúng với CPython, nhiều trình thông dịch khác không có GIL nên không gặp hạn chế này).

Khi viết code Python, ta không có quyền tác động lên GIL, nhưng các thư viện viết bằng C thì có thể quản lý GIL, chạy các OS threads riêng rẽ, và tận dụng tất cả CPU cores của hệ thống. Tuy nhiên, việc làm này là phức tạp và có ít thư viện làm như thế.

Ngoại lệ là các thư viện chuẩn xử lý I/O đều mở khóa GIL cho một luồng khác được chạy nếu như luồng hiện tại đang chờ kết quả trả về từ OS. Hệ quả là nếu sử dụng các thư viện này, ta hoàn toàn có thể lập trình đa luồng mà không bị block bởi GIL.

Đây là lý do David Beazley nói: "Đa luồng trong Python có tác dụng nhất khi chúng không làm gì".

---
### Launching Processes with concurrent.futures

Trong ví dụ tải hình ảnh cờ, do đây là tác vụ I/O bound nên việc lập trình đa luồng giúp ta tăng tốc độ xử lý lên đáng kể khi dùng thư viện chuẩn `requests`. Tuy nhiên, đối với các tác vụ thiên về tính toán hay còn gọi là CPU bound, ta cần lập trình đa tiến trình bằng việc sử dụng `ProcessPoolExecutor` của thư viện `concurrent.futures`.

Để khởi tạo đối tượng `ProcessPoolExecutor`, ta không bắt buộc phải truyền vào số lượng worker như `ThreadPoolExecutor` vì số process tối đa chính bằng số lượng CPU core trên máy của bạn, lấy về qua câu lệnh `os.cpu_count()`. Mỗi process trong pool sẽ được sử dụng một CPU core riêng, do vậy lập trình đa tiến trình có thể tối ưu các tác vụ CPU-bound bằng việc tận dụng hết số CPU core có trên hệ thống.

Dưới đây là kết quả thử nghiệm cho thấy tốc độ xử lý thuật toán mã hóa RC4 và thuật toán băm SHA - những thuật toán tiêu tốn nhiều CPU - được cải thiện đáng kể khi sử dụng số process tăng lên:

| Workers | RC4 time | RC4 factor | SHA time | SHA factor |
|---------|----------|------------|----------|------------|
| 1       | 11.48s   | 1.00x      | 22.66s   | 1.00x      |
| 2       | 8.65s    | 1.33x      | 14.90s   | 1.52x      |
| 3       | 6.04s    | 1.90x      | 11.91s   | 1.90x      |
| 4       | 5.58s    | 2.06x      | 10.89s   | 2.08x      |

Nói tóm lại, nếu muốn tăng hiệu năng của các tác vụ CPU bound, bạn nên sử dụng `ProcessPoolExecutor` với nhiều worker. Sử dụng trình thông dịch PyPy thậm chí còn cho hiệu quả cao hơn nữa.

---
### Experimenting with Executor.map

Pattern thường gặp nhất khi sử dụng `Executor.map` đó là truyền vào nó một callable và một sequence, trả về một `results` generator và lặp qua đối tượng này để thu hồi kết quả. Ví dụ:

```python
executor = futures.ThreadPoolExecutor(max_workers=3)
results = executor.map(my_callable, range(5))
for result in results:
    print(result)
```

Trong ví dụ này, ba threads đầu tiên sẽ được chạy ngay lập tức, thread thứ tư sẽ bắt đầu sau khi thread đầu tiên trả về và thread thứ năm sẽ bắt đầu khi thread thứ hai trả về.

Điểm đáng chú ý của cơ chế này là generator đầu ra luôn có thứ tự giống như sequence đầu vào. Giả sử thread 1 bị delay một khoảng thời gian dài, vòng lặp for sẽ bị stuck ở phần tử đầu tiên và ta không lấy về được giá trị nào cả. Trong lúc đó, các luồng khác đã được thực thi xong và trả về rồi, những luồng được giải phóng sẽ ngay lập tức được dùng để xử lý các phần tử tiếp theo. Như vậy, khi thread 1 hoàn thành, vòng for có thể duyệt liền một mạch trên các phần tử tiếp theo do chúng đều đã xử lý xong. 

Nếu cần giữ nguyên thứ tự đầu vào, hoặc nếu luồng xử lý chính chỉ có thể tiếp tục khi tất cả các luồng đều phải thực thi xong, việc dùng `Executor.map` là đủ hiệu quả và là đơn giản nhất.

Song, thông thường khi lập trình pipeline, ta muốn lấy về kết quả và xử lý tiếp ngay khi một luồng nào đó kết thúc, bất kể kết quả đó có đúng thứ tự hay không. Ví dụ ở [trên](#where-are-the-futures) sử dụng `Executor.submit` và `futures.as_completed` giúp ta đạt được điều đó.

Bên cạnh đó, cách dùng `submit` và `as_completed` còn linh động hơn ở chỗ ta có thể submit nhiều callable khác nhau cho một executor và gọi `as_completed` trên một list gồm các futures tạo ra bởi cả thread và process executors.

---
### Downloads with Progress Display and Error Handling

Trong mục này, ta sẽ thêm tính năng xử lý lỗi và in ra progress bar khi tải hình ảnh cờ một cách bất đồng bộ.

---
### Summary 

TBD.
