# File MOT 1.1 và chỉ số MOTA, IDF1

## 1. Bên trong file xuất MOT 1.1 của CVAT

Khi xuất **không kèm ảnh**, file zip có dạng:

```text
HoVaTen_mot.zip
└── gt/
    ├── gt.txt
    └── labels.txt     # danh sách nhãn, ở đây chỉ có "person"
```

Mỗi dòng của `gt/gt.txt` là **một box của một track ở một frame**:

```text
frame_id, track_id, x, y, w, h, not_ignored, class_id, visibility
1,        1,        1363, 569, 103, 241, 1,  1,        1
```

| Cột | Ý nghĩa |
|---|---|
| `frame_id` | Số frame, bắt đầu từ 1 |
| `track_id` | ID của track. Một người = một số duy nhất trong cả đoạn |
| `x, y` | Góc trên trái của box (pixel) |
| `w, h` | Rộng, cao của box (pixel) |
| `not_ignored` | 1 = box được tính khi chấm |
| `class_id` | Chỉ số nhãn trong `labels.txt` |
| `visibility` | Tỉ lệ nhìn thấy 0–1. Chỉ có giá trị thật nếu project có thuộc tính `visibility`; lab này không bắt điền |

Hai điều phải đúng trong file của bạn:

- Có **đúng 5 giá trị `track_id` khác nhau** (trừ khi bạn tạo track mới có ghi lý do trong báo cáo).
- Frame mà track bật `outside` **không có dòng nào**. Frame `occluded` **vẫn có dòng**.

Nguồn: [CVAT docs — MOT format](https://docs.cvat.ai/docs/dataset_management/formats/format-mot/).

## 2. Coach chấm file của bạn thế nào

Coach kiểm tra mã đề ghi trong báo cáo bằng `python src/setup_local_lab.py --mssv MSSV --assignment-only`. Tra năm MOT ID tương ứng trong `variants` của [lab_variants.json](../src/lab_variants.json), theo thứ tự P1–P5. Từ GT gốc `train/MOT17-09-DPM/gt/gt.txt`, lấy frame 1–150, năm MOT ID này, `mark=1`, `class=1` và `visibility>0`. Hàng có `visibility=0` là mốc tham chiếu cho CP2 và được bỏ khỏi tập box cần ghép, vì học viên đặt `outside` khi mất hẳn. Dùng file CVAT XML và ảnh minh chứng để soát cờ và tính liên tục của ID qua đoạn đó.

Ở mỗi frame, box của bạn được ghép với box ground truth (GT) của 5 người nếu **IoU ≥ 0,5**, mỗi box chỉ ghép một lần. Sau đó đếm:

| Ký hiệu | Đếm cái gì |
|---|---|
| GT | Tổng số box GT của 5 người, cộng mọi frame |
| FN | Box GT không được ghép (bạn bỏ sót, hoặc box trôi quá xa) |
| FP | Box của bạn không ghép được (vẽ thừa, box sai chỗ) |
| IDSW | Số lần một người thật đổi sang ID khác so với lần ghép trước |
| Frag | Số lần track của một người bị đứt rồi nối lại |

### MOTA — tổng lỗi theo từng frame

```text
MOTA = 1 − (FN + FP + IDSW) / GT
```

Ví dụ: GT = 200, FN = 20, FP = 10, IDSW = 4 → MOTA = 1 − 34/200 = **0,83**. Bốn lần đổi ID chỉ làm MOTA giảm 0,02: MOTA chủ yếu đo **detection**.

### IDF1 — mỗi người có giữ được một ID suốt đoạn không

```text
IDF1 = 2·IDTP / (2·IDTP + IDFP + IDFN)
```

Ghép **cả track với cả track**: mỗi người thật chỉ nhận đúng một ID dự đoán. Người A có 100 frame, 50 frame đầu mang ID 1, 50 frame sau mang ID 2: chỉ 50 frame được tính đúng. IDF1 phạt việc **giữ ID kém kéo dài**.

**MOTA cao không có nghĩa là ID đúng.** Muốn kết luận về ID, đọc IDSW, Frag và IDF1.

Công cụ coach dùng: [py-motmetrics](https://github.com/cheind/py-motmetrics) hoặc [TrackEval](https://github.com/JonathonLuiten/TrackEval).
