# Source code

Lab này chủ yếu làm trên CVAT. Thư mục `src/` chứa script tự kiểm và nơi đặt file xuất.

- File bắt đầu chạy: `src/check_submission.py`
- Cách chạy (từ thư mục gốc repo, Python 3.9+, không cần cài thư viện):

  ```bash
  python src/check_submission.py --mot src/exports/HoVaTen_mot.zip --cvat src/exports/HoVaTen_cvat_video.zip
  ```

  Làm bonus B1 (7 người) thì thêm `--expected 7`.
- Input: file **MOT 1.1** (`.zip` hoặc `gt.txt`) và file **CVAT for video 1.1** (`.zip` hoặc `annotations.xml`) xuất từ job của bạn, không kèm ảnh.
- Output: bảng in ra màn hình: số track ID, frame có mặt và đoạn vắng (`outside`) của từng track, số keyframe và keyframe / 100 frame, các dòng `[LỖI]` / `[CẢNH BÁO]`. Mã thoát 1 nếu còn `[LỖI]`.
- File học viên được sửa: không cần sửa script. Bạn chỉ đặt 2 file xuất vào `src/exports/`.

## Script kiểm gì

| Kiểm tra | Mức | Gợi ý lỗi tương ứng |
|---|---|---|
| Zip có kèm ảnh | LỖI | Vi phạm quy tắc dữ liệu MOT17 |
| Số track ID khác 5 | LỖI | `fragmentation`, `false_track`, thiếu người |
| Dòng sai định dạng, hai box cùng track trong một frame | LỖI | Sai định dạng xuất |
| Track vắng > 60 frame rồi xuất hiện lại | CẢNH BÁO | Trái quy ước 2 giây |
| Tâm box nhảy xa hơn nửa chiều cao box trong 1 frame | CẢNH BÁO | `id_switch`, keyframe đặt nhầm người |
| Chiều cao box đổi > 30% trong 1 frame | CẢNH BÁO | Co box theo phần nhìn thấy khi bị che |
| Hai track chồng nhau IoU > 0,7 trong ≥ 5 frame | CẢNH BÁO | Hai track một người, hoặc `merge` |
| Track chỉ có ≤ 3 frame | CẢNH BÁO | Vẽ bằng Shape thay vì Track |
| > 50 keyframe / 100 frame | CẢNH BÁO | Keyframe dày đều vô cớ |
| ≤ 2 keyframe cho > 30 frame | CẢNH BÁO | Có thể box trôi (`drift`) |

Script **không** có ground truth nên không tính MOTA / IDF1 và không biết box có bám đúng người hay không. Không có cảnh báo chưa chắc là đúng: vẫn phải tự review hai lượt (CP3).

## Số frame

Script in số frame theo CVAT, bắt đầu từ **0** (giống thanh frame trên giao diện CVAT). Trong `gt.txt`, `frame_id` = frame CVAT + 1.

## Thư mục `exports/`

Đặt đúng hai file (xem `SUBMISSION.md`):

```text
src/exports/HoVaTen_mot.zip
src/exports/HoVaTen_cvat_video.zip
```
