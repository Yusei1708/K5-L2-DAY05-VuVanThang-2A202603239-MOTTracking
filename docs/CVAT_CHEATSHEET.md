# CVAT — bảng tra nhanh cho Lab Ngày 5

Bảng phím đầy đủ trong CVAT: bấm `F1`.

## Cấu hình một lần khi mở job

1. Trên CVAT máy cá nhân, vào **Tasks**, chọn task của bạn rồi mở job duy nhất. Xem [cách tải ảnh và tạo task](CVAT_LOCAL_SETUP.md).
2. **Settings → Player**: `Player step = 10` để `V` / `C` nhảy 10 frame.
3. **Settings → Workspace**: bật hiện text của object (ID và nhãn trên box), bật auto save.

## Phím tắt

| Phím | Tác dụng |
|---|---|
| `N` | Bắt đầu / kết thúc vẽ |
| `F` / `D` | Frame sau / frame trước |
| `V` / `C` | Tới / lùi một bước (Player step) |
| `K` | Bật / tắt keyframe |
| `O` | Bật / tắt `outside` |
| `Q` | Bật / tắt `occluded` |
| `M` | Merge các track |
| `Ctrl+S` | Lưu |
| `Ctrl+B` | Propagate — **không dùng trong lab này** |

## Vẽ một track trong sáu bước

1. **Xem hết** 150 frame một lượt, ghi chỗ rẽ, dừng, bị che.
2. **Track**: Rectangle → nhãn `person` → bấm **Track** → vẽ ở frame xuất hiện đầu tiên.
3. **Nhảy step**: `V` tới 10 frame.
4. **Sửa box**: box lệch thì kéo lại cho khớp. Mỗi lần sửa CVAT tự tạo keyframe.
5. **Q / O**: bị che một phần thì `Q`, mất hẳn hoặc ra khung thì `O`. Hiện lại thì tắt `O`, chỉnh box.
6. **Tua, Save**: tua `F` từng frame qua mọi đoạn giữa hai keyframe, rồi `Ctrl+S`.

Lặp bước 3–5 tới frame cuối. Kiểm tra: panel object chỉ có **một** object mang biểu tượng track cho mỗi người, không phải hàng chục shape rời.

## Sửa lỗi ID

| Tình huống | Cách sửa |
|---|---|
| Lỡ tạo hai track cho cùng một người (ví dụ sau đoạn che) | **Merge**: bấm `M`, bấm box track thứ nhất, box track thứ hai, bấm `M` lần nữa |
| Track nhảy sang người khác | **Split** tại frame nhảy (nút cạnh Merge), rồi merge phần sau vào đúng người |
| Box trôi giữa hai keyframe | Tới frame trôi nhất, kéo box lại (thành keyframe mới) |
| Lỡ vẽ bằng Shape | Xóa, vẽ lại bằng Track |

## Xuất file

Menu job → **Export job dataset**:

1. Định dạng **MOT 1.1**, **bỏ chọn Save images** → đổi tên thành `HoVaTen_mot.zip`.
2. Định dạng **CVAT for video 1.1**, bỏ chọn Save images → đổi tên thành `HoVaTen_cvat_video.zip`. File này giữ cờ keyframe, MOT 1.1 thì không.

## CVAT chạy chậm trên máy

Đóng tab khác, dùng Chrome hoặc Edge, ẩn hoặc khóa (lock) object đã xong.
