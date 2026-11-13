# Guideline gán nhãn tracking — Lab Ngày 5

Một người thật, một track ID. Không chắc thì **ghi chú và hỏi coach**, không tự đoán rồi im lặng.

> **Số frame:** thanh frame của CVAT đếm từ **0 đến 149**. File `gt.txt` của MOT 1.1 đếm từ **1 đến 150** (`frame_id` = frame CVAT + 1). Trong báo cáo, ghi số frame **theo CVAT** (giống script `src/check_submission.py`).

## 1. Đối tượng gán

- Chỉ gán **5 người được giao** `P1`–`P5` theo bảng nhận diện mà script tạo cho đề A/B/C của bạn. Không vẽ người khác (người khác sẽ thành `false_track` / FP).
- Nhãn: `person`, công cụ **Rectangle**, chế độ **Track** (không phải Shape).
- Đặt tên hoặc ghi chú object là `P1`, `P2`… để review dễ đối chiếu.

## 2. Quy ước box

| Trường hợp | Cách gán |
|---|---|
| Người nhìn thấy rõ | Box bao **toàn thân** nhìn thấy được, từ đỉnh đầu tới gót chân, sát mép người |
| Bị che một phần (vẫn thấy một phần thân) | Box vẫn ở vị trí ước lượng của **toàn thân** (amodal box), bật `occluded` (phím `Q`). Không co box theo phần nhìn thấy |
| Bị che hoàn toàn | Bật `outside` (phím `O`) từ frame **mất hẳn** |
| Ra khỏi khung hình | Bật `outside` từ frame đầu tiên không còn thấy |
| Frame nhoè (motion blur) | Vẫn gán; box bao vùng người thật đang chiếm, không bao cả vệt nhoè |

Lý do dùng box toàn thân: ground truth của MOT17 dùng box toàn thân kèm cột `visibility`. Đổi quy ước giữa chừng làm box "co giật" khi vào và ra khỏi chỗ che, IoU với GT rơi dưới 0,5.

## 3. Cùng ID hay ID mới? (ngưỡng của lớp: 2 giây = 60 frame)

Hỏi ba câu theo thứ tự:

1. Khuất bao lâu so với ngưỡng 60 frame?
2. Ngoại hình (quần áo, dáng, kích thước, phụ kiện) có khớp không?
3. Chỗ hiện lại có đúng hướng đi và tốc độ cũ không?

| Kết quả | Cách gán |
|---|---|
| Khuất **≤ 60 frame** và chắc chắn cùng người | **Cùng track, cùng ID.** Tắt `outside` ở frame hiện lại, đặt keyframe mới |
| Khuất **> 60 frame**, hoặc không chắc cùng người | **Track mới.** Ghi vào báo cáo (mục 3) để coach quyết |
| Đi khỏi khung rồi quay lại | Áp dụng hai dòng trên, tính từ frame ra khỏi khung |

Đừng dựa riêng vào màu áo: hai người mặc giống nhau rất dễ nhầm. Xem thêm hướng đi, tốc độ, dáng, phụ kiện.

Mốc 2 giây là quy ước của lớp. Dự án thật làm theo guideline của dự án.

## 4. Đặt keyframe ở đâu (luật ngón tay cái)

Giữa hai keyframe, CVAT nội suy tuyến tính, tức là giả định **vận tốc và tốc độ đổi kích thước không đổi**:

```text
u    = (t − k0) / (k1 − k0)
b(t) = b(k0) + u × (b(k1) − b(k0))      (áp dụng cho x, y, w, h)
```

Nên đặt keyframe tại:

1. Frame đầu và frame cuối người đó có mặt.
2. Chỗ **đổi hướng**: bắt đầu rẽ, giữa khúc rẽ, hết rẽ (nội suy cắt góc).
3. Chỗ **đổi tốc độ**: bắt đầu dừng, đứng yên, đi tiếp (box đi trước hoặc sau người).
4. Chỗ **đổi kích thước** rõ: lại gần hoặc ra xa camera (box nội suy to hoặc nhỏ hơn người).
5. **Ngay trước** khi bắt đầu bị che và **ngay sau** khi hiện lại.
6. Đoạn đi thẳng đều dài: vẫn tua kiểm mỗi 10–20 frame.

Ít keyframe quá thì box trôi. Nhiều quá thì tốn công và box rung. Mức tham khảo của lớp: **khoảng 8–18 keyframe mỗi người** trên 150 frame. Trên **50 keyframe / 100 frame** ở một người là quá dày.

Ngưỡng "trôi" của lớp: box nội suy có IoU < 0,7 so với người thật thì thêm keyframe.

## 5. Bảy loại lỗi dùng khi tự review

| Mã lỗi | Dấu hiệu |
|---|---|
| `id_switch` | Cùng một ID chuyển từ người này sang người khác |
| `fragmentation` | Một người có hai ID trở lên, hoặc track đứt rồi nối bằng ID mới |
| `lost` | Người vẫn trong khung nhưng không còn box (bật `outside` quá sớm, hoặc track kết thúc sớm) |
| `merge` | Một box bao hai người đi sát nhau |
| `false_track` | Track không thuộc 5 người, hoặc box ở chỗ không có người |
| `drift` | Box trôi khỏi người giữa hai keyframe |
| `flag` | Thiếu hoặc thừa cờ `occluded` / `outside` |
