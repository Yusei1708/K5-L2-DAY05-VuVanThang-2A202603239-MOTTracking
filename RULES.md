# Rules

## Loại bài

**Cá nhân.** Mỗi học viên tự tạo task và làm trên CVAT chạy trên máy cá nhân, tự review, tự nộp một repo riêng. Được trao đổi cách dùng CVAT với bạn, nhưng **không** gán hộ, không chép file xuất của nhau.

## AI và công cụ

Được dùng:

- Trợ lý AI dạng chat để tra cứu khái niệm (MOTA, IDF1, nội suy, định dạng MOT), hỏi cách dùng CVAT, sửa câu chữ trong báo cáo.
- AI để giải thích lỗi khi chạy `src/check_submission.py`.

Không được dùng:

- Công cụ auto-annotation, tracker tự động hay model AI để **sinh box hoặc track ID** rồi nộp như nhãn của mình. Bài lab đo chính kỹ năng gán tay và quyết định ID của bạn. (Bonus B3 chỉ **xem** video tracker do coach chạy, không import kết quả vào job.)
- AI để viết hộ phần **Tự review** (mục 4) và **Ba câu kết** (mục 6). Hai mục này phải dựa trên job thật của bạn.

Bạn phải tự giải thích được, khi coach hỏi: vì sao đặt keyframe ở frame đó, vì sao giữ hay đổi ID sau đoạn che, mỗi lỗi trong bảng review là loại gì.

Nếu có dùng AI, ghi ngắn trong mục **7. Tài liệu tham khảo** của báo cáo: công cụ nào, dùng vào việc gì.

## Làm bài và liêm chính

- Không sao chép bài hoặc nhận bài làm thay.
- Ghi nguồn khi dùng tài liệu, ảnh hoặc dữ liệu bên ngoài.
- Không sửa số liệu (số keyframe, thời gian) cho đẹp. Số keyframe và thời gian là dữ liệu về chi phí gán video, không phải điểm trừ.

## Dữ liệu MOT17 và quyền riêng tư

- MOT17 dùng giấy phép **CC BY-NC-SA 3.0**: ghi nguồn, không dùng thương mại, chia sẻ lại cùng giấy phép.
- **Không commit** ảnh frame, video, hay `gt.txt` gốc của MOT17 vào repo. Xuất từ CVAT luôn **bỏ chọn Save images**.
- Lưu ảnh gốc trên máy cá nhân và chỉ đưa ảnh vào CVAT chạy trên chính máy đó. Không tải ảnh gốc lên dịch vụ CVAT công cộng.
- Ảnh chụp màn hình trong báo cáo chỉ cắt vùng cần thiết, ghi nguồn "MOT17, MOTChallenge (Milan et al., 2016)".
- Video có mặt người đi đường thật: không đăng lại ra ngoài lớp (liên hệ bài Ngày 6 về quyền riêng tư).

## Secret và tài khoản

- Không commit mật khẩu CVAT, token, file `.env`.
- Dùng tài khoản do bạn tạo trên CVAT máy cá nhân. Không chia sẻ mật khẩu.

## Nộp muộn

- Deadline mặc định: **23:59 GMT+7 ngày làm lab**, trừ khi coach thông báo deadline khác trong vòng 48h sau lab.
- Coach có thể gia hạn tối đa 48h nếu có lý do chính đáng, báo trước deadline.
- Nộp muộn không có gia hạn: **−10% điểm mỗi ngày** (tính tròn theo ngày), quá 3 ngày không nhận.
- Commit sau deadline: coach chấm theo commit cuối cùng trước deadline, trừ khi bạn chấp nhận bị trừ điểm muộn cho commit mới.

## Lỗi kỹ thuật

Nếu CVAT lỗi, mất dữ liệu, hay không xuất được file:

1. Chụp màn hình lỗi, ghi giờ.
2. Báo coach ngay trong buổi.
3. Ghi lại trong mục **5. Khó khăn** của báo cáo kèm ảnh.

Có bằng chứng thì không bị trừ điểm vì lỗi hệ thống.
