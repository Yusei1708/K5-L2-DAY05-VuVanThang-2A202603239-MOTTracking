# Tạo bài MOT17-09 trên CVAT máy cá nhân

Mỗi MSSV nhận một mã đề **A, B hoặc C**. Cả ba đề dùng cùng 150 ảnh đầu của MOT17-09 và yêu cầu theo dõi 5 người. Chạy lại với cùng MSSV sẽ ra cùng mã đề.

## 1. Chuẩn bị trước buổi

- Mở CVAT Community trên máy và kiểm tra bạn đăng nhập được tại `http://localhost:8080`. Nếu chưa có, dùng [hướng dẫn cài CVAT chính thức](https://docs.cvat.ai/docs/administration/community/basics/installation/) cho hệ điều hành của bạn.
- Cài Python **3.11 trở lên**. Clone repo rồi mở Terminal hoặc PowerShell trong thư mục repo. Nếu đã có bản clone từ trước, chạy `git pull --ff-only` để lấy bản mới trước khi tạo repo bài nộp.

```bash
git clone https://github.com/VinUni-AI20k/K5-L2-MOTTracking.git
cd K5-L2-MOTTracking
```

## 2. Chạy script tạo task

**Windows (PowerShell)**

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r src/requirements-local.txt
.\.venv\Scripts\python.exe src/setup_local_lab.py
```

**macOS hoặc Linux**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r src/requirements-local.txt
.venv/bin/python src/setup_local_lab.py
```

1. Nhập **MSSV của bạn**. Script hiện mã đề và tên task dạng `DAY05-MOT17-09-C-20241234`.
2. Script tải riêng 150 ảnh gốc (khoảng 30 MB ảnh) từ gói [MOT17Det.zip](https://motchallenge.net/data/MOT17Det.zip) và tạo bảng nhận diện trong `.lab-local/`. Mở file `de-A-P1-P5.jpg`, `de-B-P1-P5.jpg` hoặc `de-C-P1-P5.jpg` theo đường dẫn script in ra. Mỗi vòng tròn chỉ vị trí một người tại frame tham chiếu.
3. Khi được hỏi, nhập tên đăng nhập và mật khẩu **CVAT trên máy bạn**. Mật khẩu được nhập ẩn. Script tạo một task với nhãn `person` và in link **Job**. Khi đã có task trùng khớp, script mở lại job đó để bạn làm tiếp.
4. Mở link **Job**, kiểm tra có đủ frame **0–149**. Ghi mã đề vào mục **0** của báo cáo rồi bắt đầu [CP0](../CHECKPOINTS.md). Dùng bảng nhận diện để tìm P1–P5, xem cả đoạn trước khi đánh dấu frame xuất hiện đầu tiên.

Nếu CVAT chạy ở cổng khác, thêm `--server http://localhost:CỔNG` vào cuối lệnh chạy script. Nếu CVAT chưa truy cập được, bạn có thể chuẩn bị ảnh và xem mã đề trước bằng lệnh chạy script với `--prepare-only`. Để chỉ tra mã đề, chạy với `--assignment-only`.

## 3. Nếu cần tạo task bằng giao diện

1. Chạy script với `--prepare-only` để biết mã đề, tên task và tạo bảng nhận diện. Nếu mạng không cho tải riêng 150 ảnh, tải [MOT17Det.zip](https://motchallenge.net/data/MOT17Det.zip) (khoảng 2 GB), giải nén đúng `000001.jpg` đến `000150.jpg` từ `train/MOT17-09/img1/` ra ngoài repo, rồi thêm `--frames-dir "đường-dẫn-thư-mục-ảnh"` khi chạy script.
2. Trong CVAT, vào **Tasks → + → Create new task**. Dùng đúng tên task script đã in. Thêm nhãn `person`.
3. Trong **My computer → Select files**, chọn đúng 150 ảnh JPG. Trong **Advanced configuration**, chọn **Lexicographical**, đặt **Segment size = 150** và để trống **Start frame**, **Stop frame**, **Frame step**. Bấm **Submit & Open**.
4. Mở job duy nhất. CVAT frame **0** ứng với `000001.jpg`, frame **149** ứng với `000150.jpg`. Mở bảng nhận diện đúng đề và làm [CP0](../CHECKPOINTS.md).

Khi làm xong, xuất hai file theo [hướng dẫn nộp bài](../SUBMISSION.md) và bỏ chọn **Save images**. Giữ ảnh gốc và bảng nhận diện trong máy, ngoài bài nộp. Nguồn ảnh là MOT17, MOTChallenge.
