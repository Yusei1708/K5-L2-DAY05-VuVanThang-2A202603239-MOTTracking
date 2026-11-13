# Checkpoints

Năm checkpoint, làm theo thứ tự. Mốc thời gian tính bằng **phút kể từ lúc bắt đầu buổi thực hành** (phút 0), dùng được cho cả lab sáng lẫn lab chiều. Mỗi checkpoint có phần **Tự kiểm tra**: chưa đạt thì chưa sang checkpoint sau.

Quy ước nhãn đầy đủ: `docs/GUIDELINE.md`. Phím tắt: `docs/CVAT_CHEATSHEET.md`.

---

## CP0 — Mở job, cấu hình và xem trước đoạn video (phút 5–45, 40′)

- **Mục tiêu:** vào đúng job, cấu hình player, biết trước chỗ khó của 5 người trước khi vẽ.
- **Cần làm:**
  1. Mở link **Job** và bảng nhận diện P1–P5 của đề bạn nhận theo [hướng dẫn CVAT local](docs/CVAT_LOCAL_SETUP.md). Ghi mã đề vào mục **0** của báo cáo.
  2. **Settings → Player**: `Player step = 10`. **Settings → Workspace**: bật hiện text object, bật auto save.
  3. Xem hết 150 frame một lượt (`V` nhảy 10 frame = 15 màn). Ghi giờ bắt đầu.
  4. Với từng người `P1`–`P5`: ghi frame xuất hiện, frame cuối thấy được, frame rẽ / dừng / đổi tốc độ, frame bị che.
  5. Làm theo coach demo trên **người mẫu** (không thuộc 5 người): vẽ một track từ đầu tới cuối, rồi **xóa** track mẫu đó.
- **Sản phẩm:** bảng mục **1. Xem trước** trong báo cáo đã điền đủ 5 dòng.
- **Cần hiểu:** vì sao phải xem trước khi vẽ (biết chỗ nào nội suy sẽ sai để đặt keyframe ngay từ đầu).
- **Tự kiểm tra:**
  - [ ] Task có đúng một job, từ frame **0** đến **149**, với nhãn `person`.
  - [ ] Bấm `V` nhảy đúng 10 frame.
  - [ ] Trong panel object không còn track của người mẫu.

---

## CP1 — Gán 5 track trên 150 frame (phút 45–100, 55′)

- **Mục tiêu:** mỗi người `P1`–`P5` có **một** track bám đúng người trên mọi frame họ thấy được.
- **Cần làm:** với từng người (nhịp gợi ý khoảng 10 phút / người; người bị che để sau cùng):
  1. Về frame xuất hiện đầu tiên. Rectangle → nhãn `person` → bấm **Track** → vẽ sát toàn thân.
  2. Đặt tên / ghi chú object là `P1`, `P2`…
  3. `V` nhảy tới; box lệch thì kéo cho khớp (thành keyframe).
  4. Keyframe dày hơn ở chỗ đổi hướng, đổi tốc độ, đổi kích thước, quanh đoạn che; thưa ở đoạn thẳng đều.
  5. Tua `F` từng frame qua mọi đoạn giữa hai keyframe; chỗ box trôi thì thêm keyframe.
  6. Người ra khỏi khung trước frame cuối (149 trên CVAT): bật `outside` ở frame đầu tiên không còn thấy.
  7. `Ctrl+S` sau mỗi người. Ghi giờ bắt đầu, giờ kết thúc và chỗ khó vào báo cáo mục **2**.
- **Không làm:** không vẽ người ngoài 5 người; không dùng **Propagate** (`Ctrl+B`) vì nó tạo shape rời, không có ID chung.
- **Sản phẩm:** 5 track trong CVAT; bảng mục **2. Keyframe và thời gian** có thời gian từng người.
- **Cần hiểu:** keyframe là bước "sửa" sau phần "đoán" của nội suy tuyến tính; nội suy đúng khi đi thẳng đều, sai khi rẽ, tăng / giảm tốc, lại gần / ra xa camera.
- **Tự kiểm tra:**
  - [ ] Panel object có đúng **5** object, mỗi cái mang biểu tượng track (không phải hàng chục shape rời).
  - [ ] Tua `F` qua từng người: không có đoạn box trôi rõ khỏi người.
  - [ ] **Mốc phút 100:** xong ít nhất 4 người. Chưa đạt thì báo coach.

---

## CP2 — Xử lý đoạn bị che (phút 115–140, 25′)

- **Mục tiêu:** người bị che có cờ đúng và **giữ cùng ID** khi hiện lại trong vòng 2 giây.
- **Cần làm:**
  1. Theo dõi **P1**, người được chọn cho bài xử lý che khuất ở cả ba đề. Ghi 4 mốc: bắt đầu che một phần, mất hẳn, hiện lại, thấy rõ trở lại.
  2. Che một phần: bật `occluded` (`Q`); box vẫn bao toàn thân ước lượng.
  3. Mất hẳn: bật `outside` (`O`) từ frame mất hẳn. Frame hiện lại: tắt `outside`, chỉnh box, đây là keyframe mới.
  4. Áp dụng ngưỡng 60 frame (mục 3 của `docs/GUIDELINE.md`) để quyết định cùng ID hay ID mới.
  5. Lỡ tạo hai track cho cùng người: **Merge** (`M`). Track nhảy sang người khác: **Split** rồi merge đúng người.
  6. Chụp **3 ảnh màn hình** vào `report/individual/images/`: trước khi che; giữa đoạn che (thấy cờ trên panel object); sau khi hiện lại (thấy cùng ID).
- **Sản phẩm:** mục **3. Đoạn bị che** trong báo cáo, có 4 mốc frame, thời gian khuất, quyết định ID kèm lý do, 3 ảnh.
- **Cần hiểu:** trả lời được câu "Cờ `outside` để làm gì, sao không xóa box rồi vẽ track mới?" (gợi ý: nhãn GT phải nói đây vẫn là người cũ, để tracker giữ ID đúng không bị chấm sai và ReID không học rằng đó là hai người).
- **Tự kiểm tra:**
  - [ ] Ở frame giữa đoạn khuất hẳn, người đó không có box hiển thị, nhưng vẫn là cùng object trong panel.
  - [ ] ID trước và sau đoạn che giống nhau.
  - [ ] Đoạn `occluded` không bị co box theo phần nhìn thấy.

---

## CP3 — Tự review ID hai lượt (phút 140–170, 30′)

- **Mục tiêu:** tìm và sửa lỗi ID trong job của chính mình, gọi đúng tên lỗi.
- **Cần làm:** duyệt như người lạ, **ghi lỗi trước, sửa sau**.
  1. **Lượt 1, theo từng người (15′):** bật hiện ID. Với từng người, đi **ngược** từ frame 149 về frame 0 trên CVAT bằng `D` / `C`. Mỗi lượt chỉ nhìn một người, chậm lại ở chỗ hai người đi sát hoặc cắt nhau.
  2. **Lượt 2, theo cảnh (10′):** nhảy 10 frame mỗi bước bằng `V`; mỗi màn nhìn cả 5 box: ID có đổi người không, có box thừa / thiếu không.
  3. **Ghi và sửa (5′):** mỗi lỗi một dòng: frame, mã người, loại lỗi, một câu mô tả, lượt nào phát hiện. Sửa bằng Split / Merge / keyframe, đánh dấu "đã sửa", `Ctrl+S`.
- **Sản phẩm:** bảng mục **4. Tự review ID** trong báo cáo, ít nhất 3 dòng (không có lỗi thì ghi một dòng "đã kiểm hai lượt, không lỗi") và phần tổng hợp theo loại lỗi.
- **Cần hiểu:** phân biệt 7 loại lỗi trong `docs/GUIDELINE.md` mục 5; vì sao `id_switch` giữa hai người cùng lớp vẫn là lỗi nặng (vận tốc tính từ nhãn nhảy vọt, ví dụ 1,5 m trong 1/30 s ≈ 162 km/h).
- **Tự kiểm tra:**
  - [ ] Mỗi dòng trong bảng có loại lỗi đúng tên trong danh sách 7 mã.
  - [ ] Mọi lỗi đã ghi đều có cột "Đã sửa?" là có, hoặc có lý do vì sao không sửa.

---

## CP4 — Xuất file, chạy script tự kiểm, hoàn thành báo cáo (phút 170–195, 25′)

- **Mục tiêu:** có 2 file xuất đúng định dạng, đã tự kiểm bằng script, báo cáo đủ các mục.
- **Cần làm:**
  1. Export job dataset → **MOT 1.1**, bỏ chọn Save images → lưu thành `src/exports/HoVaTen_mot.zip`.
  2. Export job dataset → **CVAT for video 1.1**, bỏ chọn Save images → lưu thành `src/exports/HoVaTen_cvat_video.zip`.
  3. Chạy script tự kiểm (xem `src/README.md`):

     ```bash
     python src/check_submission.py --mot src/exports/HoVaTen_mot.zip --cvat src/exports/HoVaTen_cvat_video.zip
     ```

  4. Đọc kết quả script, sửa trên CVAT nếu có `[LỖI]`, xuất lại. Dán phần tóm tắt của script vào báo cáo mục **5**.
  5. Điền số keyframe từng người (lấy từ script) vào mục **2**, tính keyframe / 100 frame.
  6. Viết mục **6. Ba câu kết**. Ghi giờ kết thúc. Chuyển job sang **completed** trên CVAT máy cá nhân.
- **Sản phẩm:** 2 file trong `src/exports/`; báo cáo đủ mục 1–6; job ở trạng thái completed.
- **Cần hiểu:** đọc được từng cột của `gt.txt` (`docs/MOT_FORMAT.md`); vì sao frame `outside` không có dòng còn frame `occluded` vẫn có; MOTA khác IDF1 ở đâu.
- **Tự kiểm tra:**
  - [ ] Script in `Số track ID: 5` và không có dòng `[LỖI]`.
  - [ ] Không có người nào bị cảnh báo `> 50 keyframe / 100 frame`.
  - [ ] Mở `gt/gt.txt` trong zip, tìm một frame `outside` của người bị che: không có dòng nào cho ID đó.

---

## Bonus (phút 195–225, chỉ làm khi xong CP0–CP4)

Chọn tối đa hai mục, ghi vào mục **Bonus** của báo cáo. Điểm ở `RUBRIC.md`.

- **B1 — Hai người đi sát:** gán thêm 2 người đi sát nhau do coach chỉ định (chỗ dễ đổi ID nhất), mỗi người một track, không `id_switch`.
- **B2 — So cách đặt keyframe:** gán lại một người trong 5 người thành một track phụ với keyframe đều mỗi 30 frame (không chỉnh thêm). So số keyframe và chỗ box trôi với track chính đặt theo chỗ đổi hướng. Chụp ảnh frame trôi nhất. **Xóa track phụ trước khi xuất file nộp chính**, hoặc xuất riêng thành `src/exports/HoVaTen_bonus_b2.zip`.
- **B3 — So với tracker có sẵn:** xem video kết quả ByteTrack / BoT-SORT coach chạy sẵn trên cùng đoạn. Ghi 2 chỗ tracker đổi ID hoặc đứt track mà nhãn của bạn giữ đúng, giải thích mỗi chỗ bằng một ý: đoán rồi sửa (đổi tốc độ), ghép theo IoU (hai người đi sát), box score thấp (bị che), ngoại hình (áo giống nhau).
