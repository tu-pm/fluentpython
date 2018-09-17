# Coroutines

Coroutines về cú pháp rất giống generator: Chỉ đơn thuần là một hàm có từ khóa `yield`. Những đặc trưng của từ khóa `yield` trong coroutines:

*   Thường đứng bên phải một expression: `datum = yield`
*   Có thể không sinh ra giá trị nào: `yield` === `yield None`
*   Nhận giá trị truyền vào từ caller (?)

Ngay cả khi `yield` không trả về dữ liệu nào, nó cũng có thể được dùng như cờ điều khiển luồng thiết bị trong việc implement cooperative multi-tasking: mỗi coroutine yields (trả về) quyền kiểm soát cho scheduler trung tâm để các coroutines khác có thể được kích hoạt.

## How coroutines evolved from generators

PEP 342 định nghĩa ra cách implement coroutine từ generator functions với các phương thức mới được bổ sung vào generator API giúp nó có thể làm việc với coroutines, trong đó có:

*   `.send(value)`: Truyền `value` vào trong generator object
*   `.close()`: raise `GeneratorExit`
*   `.throw(exc)`: raise exeption bên trong generator
*   Cả ba phương thức này đều trả về giá trị tiếp theo được yield hoặc raise `StopIteration`

### A Simple Coroutine Generator

Hãy bắt đầu với một ví dụ đơn giản: Tạo một con đếm từ generator với tên `count2inf`:

```python
def count2inf():
    i = 0
    while True:
        x = yield i
        i += 1
        print(x)
```

Việc đặt `yield` ở bên phải dấu `=` như trong câu lệnh `x = yield i` mang ý nghĩa: "Hãy gán giá trị được truyền vào generator bởi phương thức `send` vào biến x, đồng thời `yield` ra giá trị i". Tính năng này đã biến generator object trở thành coroutine, nhận vào một chuỗi input và trả về một chuỗi kết quả xử lý. Dưới đây là một vài ví dụ sử dụng `count2inf`:

```python
>>> cnt = count2inf() #1
>>> cnt.send(3) #2
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: can't send non-None value to a just-started generator
>>> next(cnt) #3
0
>>> cnt.send(123) #4
123
1
>>> cnt.send(456)
456
2
>>> next(cnt) #5
None
3
```

*   #1: Khởi tạo một coroutine x
*   #2: Không được phép `send` giá trị khác `None` vào generator chỉ vừa mới được tạo
*   #3: Phải gọi `next` để lấy ra giá trị đầu tiên trước, đồng thời lệnh `yield` ngắt luồng xử lý ngay trước khi phép gán được thực hiện -> không lấy về được giá trị x tại lần `next` đầu tiên
*   #4: Khi gọi `cnt.send(value)`, value ghi đè lên giá trị được truyền vào generator trước đó (`None`), x được gán bằng value và được in ra, sau đó chương trình chạy đến lần `yield` tiếp theo. Tương tự lần trước, luồng xử lý bị ngắt trước khi x lấy được tham số truyền vào
*   #5: `next(cnt)` tương đương với `cnt.send(None)`

### Coroutine to compute running average

Trong chương 7, ta đã học về cách tính trung bình cộng của một running sequence. Tại đây, ta sẽ implement lại nó sử dụng coroutine

```python
def averager():
	total = 0.0
	count = 0
	average = None

	while True:
		term = yield average
		total += term
		count += 1
		average = total / count
```

Giờ ta có thể sử dụng nó bằng cách truyền tham số vào phương thức `send`:

```python
>>> coro_avg = averager()
>>> next(coro_avg)
>>> coro_avg.send(10)
10.0
>>> coro_avg.send(30)
20.0
>>> coro_avg.send(5)
15.0
```

## Decorators for coroutine priming

Trước khi sử dụng một sử dụng một coroutine, ta cần nhớ bắt đầu (prime) nó bằng cú pháp `next(x)`. Để có thể sử dụng ngay mà không cần phải nhớ thực hiện thao tác này, hãy tự động hóa nó trong một decorator:

```python
def coroutine(func):
	"""Decorator: primes `func` by advancing to first `yield`"""
	@wraps(func)
	def primer(*args, **kwargs):
		gen = func(*args, **kwargs)
		next(gen)
		return gen
	return primer
```
Giờ ta chỉ cần đặt decorator `@coroutine` trước chữ ký hàm `averager` và sử dụng nó mà không cần prime nó nữa. Tuy nhiên, phần lớn các decorator trong các coroutine framework không thực hiện prime coroutine (vì nó không hữu ích lắm).

## Coroutine termination and exception handling

Nếu một exception xảy ra bên trong coroutine, nó sẽ được chuyển về nơi gọi phương thức `next` hay `send` gây ra exception.

How an unhandled exception kills a coroutine:

```python
>>> coro_avg = averager()
>>> coro_avg.send(40)
40.0
>>> coro_avg.send(50)
45.0
>>> coro_avg.send('spam')
Traceback (most recent call last):
...
TypeError: unsupported operand type(s) for +=: 'float' and 'str'
>>> coro_avg.send(60)
Traceback (most recent call last):
File "<stdin>", line 1, in <module>
StopIteration
```

Cách hay được dùng nhất để ngừng hoạt động của coroutine đó là sử dụng phương thức `close` trên generator hoặc phương thức `throw` để tung ngoại lệ vào bên trong generator. Các thao tác bắt ngoại lệ và dọn dẹp cũng cần được thực hiện khi đóng một coroutine.

## Returning a value from a coroutine

Conroutine không chỉ có thể `yield` giá trị, nó còn có thể trả về giá trị từ lệnh `return`. Tuy nhiên việc dùng cùng lúc `yield` và `return` có thể gây nên những nhầm lẫn không đáng có. Bởi vậy, usecase thường gặp nhất khi có cả `yield` và `return` trong một coroutine là:
    *   `yield` chỉ được dùng để đọc vào giá trị mà không sinh ra giá trị nào
    *   Vòng lặp `yield` bị chấm dứt tại một điểm nào đó
    *   Hàm trả về giá trị cuối cùng với từ khóa `return`

Ví dụ: Thay đổi `averager` để nó chỉ trả về kết quả trung bình cộng cuối cùng khi nó nhận vào giá trị `None`:

```python
from collections import namedtuple

Result = namedtuple('Result', ['count', 'average'])


def averager()
	total = 0.0
	count = 0
	average = None
	while True:
		if term is None:
			break
		term = yield
		total += term
		count += 1
		average = total / count

	return Result(count, average)
```

Vấn đề của đoạn code này đó là nó trả về giá trị cuối cùng trong một ngoại lệ `StopIteration`, đây là hành động không mong muốn. Ở mục tiếp theo ta sẽ bàn đến cách xử lý vấn đề này

## Using yield from

`yield from` là một cấu trúc hoàn toàn mới trong Python, nó làm nhiều thứ hơn `yield` và việc dùng lại từ khóa này có phần misleading, một từ khóa khác kiểu như `await` phù hợp hơn là `yield from`. Một cách tổng quát, nó được dùng trong trường hợp một generator gọi đến một subgenerator, giá trị được yield bởi subgenerator sẽ trả về cho nơi gọi generator một cách trực tiếp trong khi generator cha sẽ bị block cho đến khi subgenerator kết thúc.

Trong chương 14, ta đã biết `yield from` có thể được sử dụng để yield giá trị trong vòng lặp for:

```python
for i in range(10):
    yield i
```

tương đương với

```python
yield from range(10)
```

Tất nhiên, `yield from` hữu dụng hơn thế. Tính năng chính của `yield from` đó là nó mở một kết nối hai chiều trực tiếp từ caller ngoài cùng đến generator trong cùng để các giá trị có thể được luân chuyển giữa chúng một cách trực tiếp. Dưới đây là ví dụ minh họa trực quan cho tính năng này:

![generator delegation](./images/generator-delegation.png)

Dưới đây là đoạn code đầy đủ thực thi ví dụ minh họa trên:

```python
from collections import namedtuple

Result = namedtuple('Result', 'count average')

# the subgenerator
def averager():
	total = 0.0
	count = 0
	average = None
	while True:
		term = yield
		if term is None:
			break
		total += term
		count += 1
		average = total/count
	return Result(count, average)


# the delegating generator
def grouper(results, key):
	while True:
		results[key] = yield from averager()


# the client code, a.k.a. the caller
def main(data):
	results = {}
	for key, values in data.items():
		group = grouper(results, key)
		next(group)
		for value in values:
			group.send(value)
		group.send(None) # important!

	# print(results)	# uncomment to debug
	report(results)


# output report
def report(results):
	for key, result in sorted(results.items()):
		group, unit = key.split(';')
		print('{:2} {:5} averaging {:.2f}{}'.format(
				result.count, group, result.average, unit))

data = {
	'girls;kg':
	[40.9, 38.5, 44.3, 42.2, 45.2, 41.7, 44.5, 38.0, 40.6, 44.5],
	'girls;m':
	[1.6, 1.51, 1.4, 1.3, 1.41, 1.39, 1.33, 1.46, 1.45, 1.43],
	'boys;kg':
	[39.0, 40.8, 43.2, 40.8, 43.1, 38.6, 41.4, 40.6, 36.3],
	'boys;m':
	[1.38, 1.5, 1.32, 1.25, 1.37, 1.48, 1.25, 1.49, 1.46],
}


if __name__ == '__main__':
main(data)
```

Cách thức hoạt động của module trên khá đơn giản:

*   Hàm main cần tính trung bình cộng các list item nằm trong `data` dict. Nó tạo ra `results` dict để lưu kết quả và yêu cầu `grouper` generator tính toán và đóng gói dữ liệu vào dict này
*   Với mỗi key nằm trong `data`, `grouper` tạo ra một phần tử mới trong `results` chứa kết quả được yield về từ subgenerator `averager`
*   Hàm `main` liên tục `send` giá trị vào thể hiện của `grouper` nhưng thực chất là gửi đến `averager`. Sau khi yield hết giá trị trong một list item, nó gửi `None` để break vòng lặp trong `averager` và trả lại quyền xử lý cho `grouper`
*   `grouper` nhận giá trị trả về từ `averager` và tạo ra phần tử mới trong results dict, các thao tác lại được lặp lại

Ta có thể làm chuỗi ủy nhiệm trở nên dài hơn, mỗi generator lại ủy nhiệm cho generator con của nó, kết thúc bằng một generator chỉ có mệnh đề `yield` hoặc là một `iterator`.

Chú ý rằng giá trị trả về trong mệnh đề `return` của generator trong cùng không phải là một `StopIteration` exception. Cú pháp `yield from` đã bắt, xử lý nó và chỉ trả về dữ liệu ta mong muốn (thể hiện của `Result`)

Mỗi cú pháp `yield from` đều phải được điều khiển tại vị trí gọi đến `next` hay `send` trên generator ngoài cùng: mỗi lần `yield from` tương ứng với một vòng lặp `for`.

## Coroutines for discrete event simulation

"Coroutines are a natural way of expressing many algorithms, such as simulations, games, asynchronous I/O, and other forms of event-driven programming or co-operative multitasking" - Guido van Rossum and Phillip J. Eby in PEP 342.

Ở mục này, ta sẽ đề cập đến một trong số các use cases của coroutines: *mô phỏng sự kiện*. Ta sẽ học cách xử lý các hành động concurrent sử dụng coroutine trên một luồng duy nhất. Coroutines cũng chính là nền tảng xây dựng `asyncio`, bởi vậy đây sẽ là bước khởi động tốt trước khi bàn đến concurrent programming với `asyncio` ở chương 18.

Trước hết, ta cần hiểu về khái niệm discrete event simulation (DES). Nó là một khái niệm mô phỏng trong đó trạng thái của môi trường chỉ thay đổi khi có sự kiện nào đó diễn ra. Ví dụ như các trò chơi theo lượt là DES bởi vì trạng thái của trò chơi không đổi cho đến khi người chơi quyết định nước đi mới, đối lập với các game thời gian thực khi trạng thái của trò chơi thay đổi liên tục theo thời gian thực.

Cả hai loại mô phỏng trên đều có thể được lập trình đa luồng hoặc đơn luồng sử dụng các kĩ thuật như callbacks hay coroutines điều khiển bởi một vòng lặp sự kiện (event loop). Trong đó, mô phỏng thời gian thực hay được thực hiện bởi kĩ thuật đa luồng, trong khi mô phỏng sự kiện rời rạc (DES) thường được lập trình bởi coroutines.

### The taxi fleet simulation

Kịch bản: Có n taxi, mỗi taxi thực hiện m chuyến trong ngày. Khi chưa có khách, mỗi taxi ở trong trạng thái "prowling" - tìm khách. Khi có khách rồi, nó chuyển sang trạng thái "hành trình". Sau khi trả khách, nó lại quay về trạng thái tìm khách cho đến khi thực hiện xong m chuyến thì thôi.

*Bước 1: Định nghĩa sự kiện*

```python
Event = collections.namedtuple('Event', 'time proc action')
```
Trong đó:

*   `time`: Thời điểm mà sự kiện diễn ra, được sinh bằng bộ sinh ngẫu nhiên
*   `proc`: Định danh của taxi
*   `action`={'leave garage', 'pick up passanger', 'drop off passanger', 'going home'}: Các hành động của taxi

*Bước 2: Mô phỏng một taxi*

*   Thứ tự hành động của taxi là: rời gara, lặp (đón khách, trả khách) đến khi số chuyến == m, trở về nhà. Ta sẽ lập trình một coroutine nhận vào thời điểm `time` và yield `Event` tương ứng:

    ```python
    def taxi_process(id, trips, start_time=0):
	    """Yield to simulator issuing event at each stage change"""
	    time = yield Event(start_time, id, 'leave garage')
	    for i in range(trips):
		    time = yield Event(time, id, 'pick up passager')
		    time = yield Event(time, id, 'drop off passanger')

	    yield Event(time, id, 'going home')    
    ```

*   Ta có thể tạo ra một taxi như sau:

    ```python
    >>> taxi = taxi_process(id=13, trips=2, start_time=0)
    ```
*   Bắt đầu lịch trình cho taxi này:

    ```python
    >>> next(taxi)
    Event(time=0, proc=13, action='leave garage')
    ```
*   Mỗi lần `send` vào `taxi` coroutine một thời điểm, nó sẽ sinh ra sự kiện tương ứng ở thời điểm đó

    ```python
    Event(time=0, proc=13, action='leave garage')
    >>> taxi.send(_.time + 7)
    Event(time=7, proc=13, action='pick up passenger')
    >>> taxi.send(_.time + 23)
    Event(time=30, proc=13, action='drop off passenger')
    >>> taxi.send(_.time + 5)
    Event(time=35, proc=13, action='pick up passenger')
    >>> taxi.send(_.time + 48)
    Event(time=83, proc=13, action='drop off passenger')
    >>> taxi.send(_.time + 1)
    Event(time=84, proc=13, action='going home')
    >>> taxi.send(_.time + 10)
    Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    StopIteration
    ```
*Bước 3: Tạo ra một lớp quản lý các `taxi_processes`*, các sự kiện xảy ra trước thì được hiển thị trước -> sử dụng hàng đợi ưu tiên chứa các events

*   Tạo lớp `Simulator` có hai thuộc tính là:
    *   `events`: Một `PriorityQueue` chứa các item là các đối tượng `Event` với trường khóa mặc định là `item[0]`, tức là trường `time` của `Event`
    *   `procs`: Một `dict` map giữa process id và process instance tương ứng

*   Định nghĩa phương thức `run`: Lấy ra event có `time` nhỏ nhất từ hàng đợi `events` -> in thông tin của event -> feed ngẫu nhiên thời điểm xảy ra sự kiện tiếp theo cho process có `proc.id == event.proc` -> nhận được một event mới (hoặc kết thúc process) -> nạp  event vào hàng đợi (hoặc hủy process):

    ```python
    from random import randint
    from queue import PriorityQueue

    class Simulator:

	    def __init__(self, procs_map):
		    self.events = PriorityQueue
		    self.procs = dict(procs_map)

	    def run(self, end_time):
		    """Schedule and display events until time is up"""

		    # schedule the first event for each taxi
		    for _, proc in sorted(self.procs.items()):
			    first_event = next(proc)
			    self.events.put(first_event)

		    # main loop of the simulation
		    sim_time = 0
		    while end_time > sim_time:
			    if self.events.empty():
				    print('*** end of events ***')
				    break

			    # get the event with the smallest time in the queue...
			    current_event = self.events.get()
			    sim_time, proc_id, previous_action = current_event

			    # ...and print it out
			    print('taxi: ', proc_id, proc_id * '\t', current_event)

			    # evaluate the next time an event occurs in current process...
			    next_time = sim_time + randint(1, 5)

			    # ... and generate the next event from current process
			    try:
				    next_event = self.procs[proc_id](next_time)
			    except StopIteration
				    # if there's no more events, remove reference to the process
				    del self.procs[proc_id]
			    else:
				    # put the new event on the queue
				    self.events.put(next_event)
		    else:
			    msg = '*** end of simulation time: {} events pending ***'
			    print(msg.format(self.events.qsize()))
    ```

Bước 4: Chạy chương trình:
```python
>>> taxis = {0: taxi_process(id=0, trips=2, start_time=0),
		 1: taxi_process(id=1, trips=4, start_time=5),
		 2: taxi_process(id=2, trips=6, start_time=10)}
>>> sim = Simulator(taxis)
>>> sim.run(50)
taxi:  0  Event(time=0, proc=0, action='leave garage')
taxi:  0  Event(time=3, proc=0, action='pick up passager')
taxi:  1 	 Event(time=5, proc=1, action='leave garage')
taxi:  0  Event(time=6, proc=0, action='drop off passanger')
taxi:  1 	 Event(time=6, proc=1, action='pick up passager')
taxi:  0  Event(time=10, proc=0, action='pick up passager')
taxi:  2 		 Event(time=10, proc=2, action='leave garage')
taxi:  1 	 Event(time=11, proc=1, action='drop off passanger')
taxi:  0  Event(time=13, proc=0, action='drop off passanger')
taxi:  2 		 Event(time=13, proc=2, action='pick up passager')
taxi:  1 	 Event(time=14, proc=1, action='pick up passager')
taxi:  0  Event(time=15, proc=0, action='going home')
taxi:  2 		 Event(time=15, proc=2, action='drop off passanger')
taxi:  1 	 Event(time=17, proc=1, action='drop off passanger')
taxi:  2 		 Event(time=17, proc=2, action='pick up passager')
taxi:  1 	 Event(time=21, proc=1, action='pick up passager')
taxi:  2 		 Event(time=21, proc=2, action='drop off passanger')
taxi:  1 	 Event(time=23, proc=1, action='drop off passanger')
taxi:  2 		 Event(time=26, proc=2, action='pick up passager')
taxi:  1 	 Event(time=28, proc=1, action='pick up passager')
taxi:  2 		 Event(time=29, proc=2, action='drop off passanger')
taxi:  1 	 Event(time=30, proc=1, action='drop off passanger')
taxi:  2 		 Event(time=32, proc=2, action='pick up passager')
taxi:  1 	 Event(time=35, proc=1, action='going home')
taxi:  2 		 Event(time=37, proc=2, action='drop off passanger')
taxi:  2 		 Event(time=39, proc=2, action='pick up passager')
taxi:  2 		 Event(time=44, proc=2, action='drop off passanger')
taxi:  2 		 Event(time=46, proc=2, action='pick up passager')
taxi:  2 		 Event(time=48, proc=2, action='drop off passanger')
taxi:  2 		 Event(time=51, proc=2, action='going home')
*** end of simulation time: 0 events pending ***
```
## Coroutine Applications

Dưới đây là note về coroutine của tôi về bài giảng [Curious Course on Coroutines and Concurrency](https://www.youtube.com/watch?v=Z_OAlIhXziw) nói về các ứng dụng của coroutine:

*   Part I: Introduction to Generators and Coroutines
    *   Generators tạo ra giá trị, coroutines nhận vào giá trị
    *   Không trộn lẫn hai khái niệm này để tránh gây khó hiểu
*   Part II: Coroutines, Pipelines, and Dataflow
    *   Tạo ra pipeline bằng coroutines, bao gồm một điểm đầu sinh ra giá trị feed vào pipeline, các coroutines nhận vào, xử lý và truyền đi giá trị, một điểm cuối hiển thị giá trị cuối cùng và xử lý đóng pipeline (với phương thức `close`)
    *   Có thể rẽ nhánh, gộp nhánh các pipelines để tạo thành một dataflow graph
    *   Về mặt khái niệm, coroutines giống với handler desgin pattern trong lập trình hướng đối tượng: Đều nhận dữ liệu từ một nguồn nào đó và gửi đi tới các đích khác nhau
*   Part III: Coroutines and Event Dispatching
    *   Có thể dùng coroutines cho các hệ thống event driven
    *   Ý tưởng chính:
        1.  Tiền xử lý input thành format (event, data) và gửi output cho coroutine xử lý dữ liệu
        1.  Coroutine đọc dữ liệu, xử lý dữ liệu dựa vào event và gửi dữ liệu đến (các) điểm cuối. Bản chất coroutine này là một state machine - quay trở lại trạng thái ban đầu khi đã xử lý + gửi dữ liệu xong
        1.  Các điểm cuối hiển thị dữ liệu + kết thúc pipeline
*   Part IV: From Data Processing to Concurrent Programming
    *   Có thể gửi dữ liệu đến các coroutines nằm trên các threads/processes/hosts khác
    *   Một vài chú ý:
        *   Gửi dữ liệu đến một coroutine đang chạy gây ra ngoại lệ và ngừng chương trình
        *   Không thể gửi ngược dữ liệu đến coroutine nguồn, cũng không thể gửi lại dữ liệu từ coroutine cho chính nó
*   Part V: Coroutines as Tasks
    *   Trong lập trình concurrent, task là một vấn đề con có các tính chất:
        *   Kiểm soát luồng độc lập
        *   Sở hữu trạng thái nội bộ
        *   Có thể được lập lịch (tạm dừng,  tiếp tục)
        *   Có thể giao tiếp với các tasks khác
    *   Do vậy, coroutines cũng là tasks
    *   Tuy nhiên, coroutines không nhất thiết là đa luồng hay đa tiến trình => Có thể lập trình mustitasking chỉ với một luồng duy nhất sử dụng coroutine
*   Part VI: A Crash Course of OS
    *   Công việc phân công và quản lý multitask là của hệ điều hành
    *   Hệ điều hành luân chuyển giữa các tasks nhờ cơ chế trap (sinh bởi tín hiệu phần cứng hoặc phần mềm), yêu cầu tạm dừng tiến trình hiện tại và chuyển sang thực hiện tiến trình khác
    *   Các tasks chờ đợi để được thực thi trong các hàng đợi
    *   Bản chất câu lệnh `yield` cũng là một dạng trap: Quá trình thực thi bên trong generator bị dừng lại khi tới lệnh yield, quyền kiểm soát chuyển về cho phía gọi generator (phương thức `next` hay `send`)
    *   Hãy thử xây dựng một hệ điều hành đa nhiệm sử dụng coroutine!
*   Part VII: Let's Build an Operating System
    *   Just kidding :v Look at his code if you're interested
*   Part VIII: The Problem with the Stack
    *   Mệnh đề `yield` chỉ có thể tạm dừng hàm chứa nó, không thể dùng để ngừng tác vụ ở mức sâu hơn
