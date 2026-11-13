# Submission

## Loại bài

**Cá nhân.** Mỗi học viên tự nộp repo của mình.

## Tên repo

Repo đề bài (dùng chung cho level 2):

```text
K5-L2-MOTTracking
```

Repo bài nộp của bạn:

```text
K5-L2-DAY05-HoVaTen-MSSV-MOTTracking
```

Ví dụ: `K5-L2-DAY05-NguyenVanAn-20241234-MOTTracking`.

- Viết không dấu, không khoảng trắng; ngăn cách các phần bằng dấu `-`.
- Ngày học dùng hai chữ số: `DAY05`.
- Nếu lớp bạn tách A / B và coach yêu cầu, thay `L2` bằng `L2A` hoặc `L2B`.

## Cấu trúc và file phải nộp

```text
K5-L2-DAY05-HoVaTen-MSSV-MOTTracking/
├── src/exports/
│   ├── HoVaTen_mot.zip            # BẮT BUỘC: MOT 1.1, không kèm ảnh
│   ├── HoVaTen_cvat_video.zip     # BẮT BUỘC: CVAT for video 1.1, không kèm ảnh
│   └── HoVaTen_bonus_b2.zip       # chỉ khi làm bonus B2 và xuất riêng
└── report/individual/
    ├── 20241234_NguyenVanAn.md    # BẮT BUỘC: đổi tên từ MSSV_HoTen.md
    └── images/                    # BẮT BUỘC: ít nhất 3 ảnh đoạn bị che
```

| File | Yêu cầu |
|---|---|
| `src/exports/HoVaTen_mot.zip` | Xuất từ CVAT, định dạng **MOT 1.1**, bỏ chọn Save images. Bên trong có `gt/gt.txt` |
| `src/exports/HoVaTen_cvat_video.zip` | Xuất từ CVAT, định dạng **CVAT for video 1.1**, bỏ chọn Save images. Bên trong có `annotations.xml` |
| `report/individual/MSSV_HoTen.md` | Đổi tên theo MSSV và họ tên không dấu, ví dụ `20241234_NguyenVanAn.md`. Ghi mã đề A/B/C ở mục 0 và điền đủ mục 1–6 |
| `report/individual/images/` | 3 ảnh đoạn bị che (trước, giữa, sau), đặt tên `che_1_truoc.png`, `che_2_giua.png`, `che_3_sau.png` |

Trên CVAT máy cá nhân, chuyển job sang **completed**. Coach xem bài qua repo đã nộp.

**Không nộp:** ảnh frame, bảng nhận diện P1–P5, video, `gt.txt` gốc của MOT17, file `.env`, mật khẩu.

## Nơi nộp

1. Push repo lên GitHub (để public hoặc mời coach vào repo private, theo hướng dẫn của coach).
2. Nộp **link repo** trên LMS bằng tài khoản cá nhân.

## Deadline (GMT+7)

- **23:59 GMT+7 ngày làm lab.**
- Nếu coach thông báo deadline khác trong vòng 48h sau lab, làm theo thông báo đó.
- Nộp muộn: xem `RULES.md`.

## Cách kiểm tra trước khi nộp

Chạy script tự kiểm từ thư mục gốc của repo:

```bash
python src/check_submission.py --mot src/exports/HoVaTen_mot.zip --cvat src/exports/HoVaTen_cvat_video.zip
```

Đạt khi: script in `Số track ID: 5`, không có dòng `[LỖI]`.

Kiểm tra không lỡ commit ảnh MOT17:

```bash
git ls-files | grep -iE "\.(jpg|jpeg|png|mp4)$"
```

Lệnh chỉ được in ra các ảnh chụp màn hình trong `report/individual/images/`.

## Checklist

- [ ] Repo đặt đúng tên `K5-L2-DAY05-HoVaTen-MSSV-MOTTracking`.
- [ ] Có `src/exports/HoVaTen_mot.zip` (MOT 1.1) và `src/exports/HoVaTen_cvat_video.zip` (CVAT for video 1.1), cả hai không kèm ảnh.
- [ ] Script tự kiểm báo 5 track ID, không có `[LỖI]`; đã dán kết quả vào báo cáo mục 5.
- [ ] Báo cáo đã đổi tên thành `MSSV_HoTen.md` và điền đủ mục 1–6.
- [ ] Có 3 ảnh đoạn bị che trong `report/individual/images/` và đã chèn vào báo cáo.
- [ ] Job trên CVAT máy cá nhân đã chuyển sang **completed**.
- [ ] Không commit ảnh / video / `gt.txt` gốc của MOT17, không commit `.env` hay mật khẩu.
- [ ] Đã nộp link repo trên LMS trước 23:59 GMT+7 ngày lab.
