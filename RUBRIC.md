# Rubric

Chấm theo từng học viên. **Đạt: từ 70/100 điểm chính và không còn `id_switch` nào chưa giải thích trong báo cáo.**

Coach dùng MSSV để [xác nhận mã đề và lọc đúng 5 người](docs/MOT_FORMAT.md#2-coach-chấm-file-của-bạn-thế-nào). Sau đó so file MOT 1.1 của bạn với ground truth của 5 người mục tiêu: ghép theo IoU ≥ 0,5 ở từng frame, đếm FN, FP, IDSW, Frag, tính MOTA và IDF1; đếm keyframe từ file CVAT for video 1.1; đối chiếu bảng tự review trong báo cáo với lỗi thật tìm được.

## Điểm chính (100)

| Tiêu chí | Điểm | Bằng chứng | Điều kiện được điểm / bị trừ |
|---|---:|---|---|
| C1 — Đủ 5 track, đúng người (CP1) | 15 | `src/exports/*_mot.zip` | 5 track, mỗi track bám đúng người mục tiêu. −3 mỗi người thiếu hoặc nhầm người |
| C2 — Giữ ID: IDSW, Frag (CP1, CP3) | 25 | `*_mot.zip` so với GT | IDSW = 0, Frag = 0 sau khi sửa. −5 mỗi IDSW; −3 mỗi lần đứt track không có lý do ghi trong báo cáo |
| C3 — Chất lượng box: FN, FP ở IoU ≥ 0,5 (CP1) | 15 | `*_mot.zip` so với GT | Ít nhất 90% box GT của 5 người được ghép. −1 mỗi 2% dưới 90%; −1 mỗi 5 box thừa |
| C4 — Đoạn bị che (CP2) | 15 | `*_mot.zip`, báo cáo mục 3, 3 ảnh trong `report/individual/images/` | `occluded` và `outside` đúng đoạn, cùng ID khi hiện lại. −5 nếu tạo track mới sai quy ước 60 frame; −3 thiếu hoặc thừa cờ; −2 thiếu ảnh |
| C5 — Keyframe hợp lý (CP1) | 10 | `*_cvat_video.zip`, báo cáo mục 2 | Keyframe ở chỗ rẽ, dừng, đổi kích thước, quanh đoạn che; không dày đều vô cớ. −3 nếu > 50 keyframe / 100 frame ở một người; −3 nếu box trôi rõ giữa hai keyframe |
| C6 — Tự review (CP3) | 10 | Báo cáo mục 4 | Bảng có đủ hai lượt, đúng tên loại lỗi. −2 mỗi lỗi ID dễ thấy còn trong file nộp mà bảng không ghi; −2 mỗi lỗi gán sai loại; −4 nếu bảng trống mà không ghi "đã kiểm hai lượt" |
| C7 — File xuất và tự kiểm (CP4) | 5 | `src/exports/`, báo cáo mục 5 | MOT 1.1 mở được, đúng 5 track ID; có CVAT for video 1.1; có kết quả script. −3 sai định dạng; −2 thiếu file thứ hai; −1 không dán kết quả script |
| C8 — Báo cáo (CP0–CP4) | 5 | `report/individual/MSSV_HoTen.md` | Đủ mục 1–6: xem trước, số keyframe, thời gian, ba câu kết. −1 mỗi mục thiếu |
| **Tổng điểm chính** | **100** | | |

## Bonus (tối đa 10, ghi riêng, không tự cộng vào điểm chính)

| Mục | Điểm tối đa | Bằng chứng | Điều kiện |
|---|---:|---|---|
| B1 — Hai người đi sát | 5 | `*_mot.zip` có thêm 2 track, báo cáo mục Bonus | 2 track đúng người, IDSW = 0 giữa hai người |
| B2 — So cách đặt keyframe | 5 | Báo cáo mục Bonus, ảnh frame trôi nhất | Có số keyframe hai cách, chỉ ra được frame trôi và giải thích bằng giả định vận tốc không đổi |
| B3 — So với tracker có sẵn | 5 | Báo cáo mục Bonus | 2 chỗ khác nhau, mỗi chỗ có frame, mã người, tracker làm gì, giải thích bằng đúng một ý trong bốn ý |

Bonus chỉ được tính khi CP0–CP4 đã hoàn thành. Bonus là điểm cộng cho bài lab, không phải điểm phát biểu hay giơ tay.

## Điều kiện mất điểm chung

- Repo hoặc file báo cáo đặt sai tên: coach có thể không tìm thấy bài; nếu vẫn chấm được, −5 điểm.
- Commit ảnh, video hoặc `gt.txt` gốc của MOT17 vào repo: −10 điểm và phải xóa khỏi lịch sử git.
- Nộp muộn: theo `RULES.md`.
- Sao chép annotation của người khác (file xuất trùng gần như hoàn toàn): 0 điểm cho cả hai bài.
