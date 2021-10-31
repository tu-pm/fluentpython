### Coroutine Applications

Dưới đây là note về coroutine của tôi về bài giảng [Curious Course on Coroutines and Concurrency](https://www.youtube.com/watch?v=Z_OAlIhXziw) nói về các ứng dụng của coroutine:

-   Part I: Introduction to Generators and Coroutines
    -   Generators tạo ra giá trị, coroutines nhận vào giá trị
    -   Không trộn lẫn hai khái niệm này để tránh gây khó hiểu
-   Part II: Coroutines, Pipelines, and Dataflow
    -   Tạo ra pipeline bằng coroutines, bao gồm một điểm đầu sinh ra giá trị feed vào pipeline, các coroutines nhận vào, xử lý và truyền đi giá trị, một điểm cuối hiển thị giá trị cuối cùng và xử lý đóng pipeline (với phương thức `close`)
    -   Có thể rẽ nhánh, gộp nhánh các pipelines để tạo thành một dataflow graph
    -   Về mặt khái niệm, coroutines giống với handler desgin pattern trong lập trình hướng đối tượng: Đều nhận dữ liệu từ một nguồn nào đó và gửi đi tới các đích khác nhau
-   Part III: Coroutines and Event Dispatching
    -   Có thể dùng coroutines cho các hệ thống event driven
    -   Ý tưởng chính:
        1.  Tiền xử lý input thành format (event, data) và gửi output cho coroutine xử lý dữ liệu
        1.  Coroutine đọc dữ liệu, xử lý dữ liệu dựa vào event và gửi dữ liệu đến (các) điểm cuối. Bản chất coroutine này là một state machine - quay trở lại trạng thái ban đầu khi đã xử lý + gửi dữ liệu xong
        1.  Các điểm cuối hiển thị dữ liệu + kết thúc pipeline
-   Part IV: From Data Processing to Concurrent Programming
    -   Có thể gửi dữ liệu đến các coroutines nằm trên các threads/processes/hosts khác
    -   Một vài chú ý:
        -   Gửi dữ liệu đến một coroutine đang chạy gây ra ngoại lệ và ngừng chương trình
        -   Không thể gửi ngược dữ liệu đến coroutine nguồn, cũng không thể gửi lại dữ liệu từ coroutine cho chính nó
-   Part V: Coroutines as Tasks
    -   Trong lập trình concurrent, task là một vấn đề con có các tính chất:
        -   Kiểm soát luồng độc lập
        -   Sở hữu trạng thái nội bộ
        -   Có thể được lập lịch (tạm dừng,  tiếp tục)
        -   Có thể giao tiếp với các tasks khác
    -   Do vậy, coroutines cũng là tasks
    -   Tuy nhiên, coroutines không nhất thiết là đa luồng hay đa tiến trình => Có thể lập trình mustitasking chỉ với một luồng duy nhất sử dụng coroutine
-   Part VI: A Crash Course of OS
    -   Công việc phân công và quản lý multitask là của hệ điều hành
    -   Hệ điều hành luân chuyển giữa các tasks nhờ cơ chế trap (sinh bởi tín hiệu phần cứng hoặc phần mềm), yêu cầu tạm dừng tiến trình hiện tại và chuyển sang thực hiện tiến trình khác
    -   Các tasks chờ đợi để được thực thi trong các hàng đợi
    -   Bản chất câu lệnh `yield` cũng là một dạng trap: Quá trình thực thi bên trong generator bị dừng lại khi tới lệnh yield, quyền kiểm soát chuyển về cho phía gọi generator (phương thức `next` hay `send`)
    -   Hãy thử xây dựng một hệ điều hành đa nhiệm sử dụng coroutine!
-   Part VII: Let's Build an Operating System
    -   Just kidding :v Look at his code if you're interested
-   Part VIII: The Problem with the Stack
    -   Mệnh đề `yield` chỉ có thể tạm dừng hàm chứa nó, không thể dùng để ngừng tác vụ ở mức sâu hơn