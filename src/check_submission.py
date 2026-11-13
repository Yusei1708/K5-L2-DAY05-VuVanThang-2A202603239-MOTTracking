"""Tự kiểm file xuất của Lab Ngày 5 (MOT 1.1 và CVAT for video 1.1).

Chỉ dùng thư viện chuẩn của Python 3.9+, không cần cài thêm gì.

Ví dụ:
    python src/check_submission.py --mot src/exports/HoVaTen_mot.zip
    python src/check_submission.py --mot src/exports/HoVaTen_mot.zip --cvat src/exports/HoVaTen_cvat_video.zip

Script KHÔNG có ground truth nên không tính MOTA / IDF1. Nó chỉ bắt các lỗi
định dạng và các dấu hiệu nghi ngờ (đoạn khuất quá dài, box nhảy, hai track
chồng nhau, keyframe quá dày) để bạn mở lại CVAT kiểm tra.

Quy ước số frame: script in số frame theo CVAT (bắt đầu từ 0, giống thanh
frame trên giao diện). Trong gt.txt, frame_id = frame CVAT + 1.
"""

from __future__ import annotations

import argparse
import io
import sys
import xml.etree.ElementTree as ET
import zipfile
from collections import defaultdict
from pathlib import Path

NUM_FRAMES = 150          # số frame của đoạn lab
IMG_W, IMG_H = 1920, 1080  # độ phân giải MOT17-09
GAP_LIMIT = 60            # ngưỡng 2 giây ở 30 fps
KF_DENSITY_LIMIT = 50.0   # keyframe / 100 frame
OVERLAP_IOU = 0.7         # hai track chồng nhau quá mức này -> nghi merge / trùng track
OVERLAP_MIN_FRAMES = 5
JUMP_RATIO = 0.5          # tâm box dịch > 0.5 × chiều cao box trong 1 frame -> nghi nhảy ID
SIZE_RATIO = 1.3          # chiều cao box đổi > 30% trong 1 frame -> nghi co giật


class Report:
    def __init__(self) -> None:
        self.errors = 0
        self.warnings = 0

    def ok(self, msg: str) -> None:
        print(f"  [OK]        {msg}")

    def warn(self, msg: str) -> None:
        self.warnings += 1
        print(f"  [CẢNH BÁO]  {msg}")

    def error(self, msg: str) -> None:
        self.errors += 1
        print(f"  [LỖI]       {msg}")

    def info(self, msg: str) -> None:
        print(f"              {msg}")


def read_member(path: Path, wanted_suffix: str) -> str:
    """Đọc file text: trực tiếp, hoặc file đầu tiên trong zip có đuôi wanted_suffix."""
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as zf:
            names = [n for n in zf.namelist() if n.replace("\\", "/").endswith(wanted_suffix)]
            if not names:
                raise FileNotFoundError(
                    f"Không thấy '{wanted_suffix}' trong {path.name}. Có: {zf.namelist()}"
                )
            with zf.open(names[0]) as fh:
                return io.TextIOWrapper(fh, encoding="utf-8").read()
    return path.read_text(encoding="utf-8")


def zip_has_images(path: Path) -> bool:
    if path.suffix.lower() != ".zip":
        return False
    with zipfile.ZipFile(path) as zf:
        return any(n.lower().endswith((".jpg", ".jpeg", ".png")) for n in zf.namelist())


def iou(a: tuple, b: tuple) -> float:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    ix = max(0.0, min(ax + aw, bx + bw) - max(ax, bx))
    iy = max(0.0, min(ay + ah, by + bh) - max(ay, by))
    inter = ix * iy
    union = aw * ah + bw * bh - inter
    return inter / union if union > 0 else 0.0


def segments(frames: list[int]) -> list[tuple[int, int]]:
    """[1,2,3,7,8] -> [(1,3),(7,8)]"""
    out: list[tuple[int, int]] = []
    for f in frames:
        if out and f == out[-1][1] + 1:
            out[-1] = (out[-1][0], f)
        else:
            out.append((f, f))
    return out


def fmt_segments(segs: list[tuple[int, int]]) -> str:
    return ", ".join(f"{a}–{b}" if a != b else f"{a}" for a, b in segs)


# ---------------------------------------------------------------------------
# MOT 1.1
# ---------------------------------------------------------------------------

def check_mot(path: Path, expected: int, rep: Report) -> None:
    print(f"\n=== File MOT 1.1: {path.name} ===")
    if zip_has_images(path):
        rep.error("Zip có kèm ảnh. Xuất lại và bỏ chọn 'Save images' (không được nộp ảnh MOT17).")

    try:
        text = read_member(path, "gt/gt.txt") if path.suffix.lower() == ".zip" else read_member(path, "")
    except (FileNotFoundError, zipfile.BadZipFile) as exc:
        rep.error(f"Không đọc được gt.txt: {exc}. Bạn đã chọn đúng định dạng MOT 1.1 chưa?")
        return

    boxes: dict[int, dict[int, tuple]] = defaultdict(dict)  # track -> frame(0-based) -> (x,y,w,h)
    bad_lines = 0
    dup = 0
    for lineno, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(",")]
        try:
            frame_id, tid = int(float(parts[0])), int(float(parts[1]))
            x, y, w, h = (float(v) for v in parts[2:6])
        except (ValueError, IndexError):
            bad_lines += 1
            if bad_lines <= 3:
                rep.error(f"Dòng {lineno} sai định dạng: '{line}'")
            continue
        f = frame_id - 1
        if f in boxes[tid]:
            dup += 1
        boxes[tid][f] = (x, y, w, h)

    if bad_lines:
        rep.error(f"Tổng cộng {bad_lines} dòng sai định dạng.")
    if dup:
        rep.error(f"{dup} lần một track có hai box trong cùng một frame.")
    if not boxes:
        rep.error("gt.txt không có box nào.")
        return

    n = len(boxes)
    total = sum(len(v) for v in boxes.values())
    print(f"  Số track ID: {n}   |   Tổng số box: {total}")
    if n == expected:
        rep.ok(f"Đúng {expected} track ID.")
    elif n > expected:
        rep.error(
            f"Có {n} track ID, cần {expected}. Thừa track = fragmentation (một người hai ID) "
            "hoặc false_track (vẽ người ngoài danh sách). Nếu cố ý tạo track mới, ghi lý do vào báo cáo mục 3."
        )
    else:
        rep.error(f"Có {n} track ID, cần {expected}. Thiếu người hoặc đã merge nhầm hai người.")

    print("\n  Track | Frame có mặt | Số frame | Đoạn vắng (outside)")
    for tid in sorted(boxes):
        frames = sorted(boxes[tid])
        segs = segments(frames)
        gaps = [(segs[i][1] + 1, segs[i + 1][0] - 1) for i in range(len(segs) - 1)]
        gap_txt = fmt_segments(gaps) if gaps else "-"
        print(f"  {tid:>5} | {frames[0]:>3}–{frames[-1]:<3}      | {len(frames):>8} | {gap_txt}")

    print()
    for tid in sorted(boxes):
        tb = boxes[tid]
        frames = sorted(tb)
        segs = segments(frames)

        out_of_range = [f for f in frames if f < 0 or f >= NUM_FRAMES]
        if out_of_range:
            rep.error(f"Track {tid}: frame ngoài khoảng 0–{NUM_FRAMES - 1}: {out_of_range[:5]}")

        if len(frames) <= 3:
            rep.warn(f"Track {tid} chỉ có {len(frames)} frame: có thể là shape rời hoặc track thừa.")

        for i in range(len(segs) - 1):
            gap = segs[i + 1][0] - segs[i][1] - 1
            if gap > GAP_LIMIT:
                rep.warn(
                    f"Track {tid}: vắng {gap} frame (frame {segs[i][1] + 1}–{segs[i + 1][0] - 1}) "
                    f"> {GAP_LIMIT}. Quy ước lớp: khuất quá 2 giây thì tạo track mới, hoặc ghi lý do."
                )

        for f, (x, y, w, h) in tb.items():
            if w <= 0 or h <= 0:
                rep.error(f"Track {tid} frame {f}: box rộng hoặc cao <= 0.")
                break
            if x + w < 0 or y + h < 0 or x > IMG_W or y > IMG_H:
                rep.warn(f"Track {tid} frame {f}: box nằm hẳn ngoài ảnh. Nên bật outside thay vì để box ngoài khung.")
                break

        jumps, resizes = [], []
        for f in frames:
            if f + 1 not in tb:
                continue
            x0, y0, w0, h0 = tb[f]
            x1, y1, w1, h1 = tb[f + 1]
            dc = ((x1 + w1 / 2 - x0 - w0 / 2) ** 2 + (y1 + h1 / 2 - y0 - h0 / 2) ** 2) ** 0.5
            if dc > JUMP_RATIO * max(h0, h1):
                jumps.append(f + 1)
            if max(h0, h1) / max(1e-6, min(h0, h1)) > SIZE_RATIO:
                resizes.append(f + 1)
        if jumps:
            rep.warn(f"Track {tid}: box nhảy xa trong 1 frame ở frame {jumps[:5]}. Kiểm tra id_switch hoặc keyframe đặt nhầm người.")
        if resizes:
            rep.warn(f"Track {tid}: chiều cao box đổi > 30% trong 1 frame ở frame {resizes[:5]}. Kiểm tra box co giật (co box theo phần nhìn thấy?).")

    ids = sorted(boxes)
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            common = set(boxes[a]) & set(boxes[b])
            hits = [f for f in sorted(common) if iou(boxes[a][f], boxes[b][f]) > OVERLAP_IOU]
            if len(hits) >= OVERLAP_MIN_FRAMES:
                rep.warn(
                    f"Track {a} và {b} chồng nhau (IoU > {OVERLAP_IOU}) ở {len(hits)} frame, "
                    f"ví dụ frame {hits[:3]}. Có thể hai track cùng một người, hoặc box merge hai người."
                )


# ---------------------------------------------------------------------------
# CVAT for video 1.1
# ---------------------------------------------------------------------------

def check_cvat(path: Path, rep: Report) -> None:
    print(f"\n=== File CVAT for video 1.1: {path.name} ===")
    if zip_has_images(path):
        rep.error("Zip có kèm ảnh. Xuất lại và bỏ chọn 'Save images'.")
    try:
        text = read_member(path, "annotations.xml")
        root = ET.fromstring(text)
    except (FileNotFoundError, zipfile.BadZipFile, ET.ParseError) as exc:
        rep.error(f"Không đọc được annotations.xml: {exc}. Bạn đã chọn đúng định dạng CVAT for video 1.1 chưa?")
        return

    tracks = root.findall("track")
    loose = root.findall("image")
    if loose:
        rep.warn("File có thẻ <image>: có vẻ đây là 'CVAT for images', không phải 'CVAT for video'.")
    if not tracks:
        rep.error("Không có track nào. Bạn đã vẽ bằng Track (không phải Shape) chưa?")
        return

    print("\n  Track | Nhãn   | Frame thấy | Keyframe | KF/100 frame | Frame occluded | Lần bật outside")
    total_kf = total_vis = 0
    for tr in tracks:
        tid = tr.get("id")
        label = tr.get("label", "?")
        boxes = tr.findall("box")
        if not boxes:
            rep.warn(f"Track {tid} không phải rectangle (không có <box>).")
            continue
        vis = [b for b in boxes if b.get("outside") == "0"]
        kf = [b for b in vis if b.get("keyframe") == "1"]
        occ = [b for b in vis if b.get("occluded") == "1"]
        boxes_sorted = sorted(boxes, key=lambda b: int(b.get("frame")))
        out_events = sum(
            1 for prev, cur in zip(boxes_sorted, boxes_sorted[1:])
            if prev.get("outside") == "0" and cur.get("outside") == "1"
        )
        n_vis = len(vis)
        density = 100.0 * len(kf) / n_vis if n_vis else 0.0
        total_kf += len(kf)
        total_vis += n_vis
        print(f"  {tid:>5} | {label:<6} | {n_vis:>10} | {len(kf):>8} | {density:>12.1f} | {len(occ):>14} | {out_events:>15}")
        kf_frames = sorted(int(b.get("frame")) for b in kf)
        rep.info(f"Track {tid}: keyframe ở frame {kf_frames}")

        if label != "person":
            rep.warn(f"Track {tid} có nhãn '{label}', lab này chỉ dùng 'person'.")
        if n_vis <= 3:
            rep.warn(f"Track {tid} chỉ thấy {n_vis} frame: có thể là shape rời (vẽ bằng Shape) hoặc track thừa.")
        if density > KF_DENSITY_LIMIT:
            rep.warn(f"Track {tid}: {density:.0f} keyframe / 100 frame > {KF_DENSITY_LIMIT:.0f}. Quá dày, dồn keyframe vào chỗ rẽ / dừng / bị che.")
        elif n_vis > 30 and len(kf) <= 2:
            rep.warn(f"Track {tid}: chỉ {len(kf)} keyframe cho {n_vis} frame. Đã tua F kiểm tra box trôi chưa?")

    if total_vis:
        print(f"\n  Tổng: {total_kf} keyframe / {total_vis} frame có mặt = {100.0 * total_kf / total_vis:.1f} keyframe / 100 frame")
    rep.ok(f"Đọc được {len(tracks)} track từ annotations.xml.")


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # console Windows mặc định không in được tiếng Việt
        except (AttributeError, ValueError):
            pass
    ap =argparse.ArgumentParser(description="Tự kiểm file xuất Lab Ngày 5 (MOT 1.1, CVAT for video 1.1).")
    ap.add_argument("--mot", type=Path, help="File MOT 1.1 (.zip) hoặc gt.txt")
    ap.add_argument("--cvat", type=Path, help="File CVAT for video 1.1 (.zip) hoặc annotations.xml")
    ap.add_argument("--expected", type=int, default=5, help="Số track mong đợi (mặc định 5; làm bonus B1 thì 7)")
    args = ap.parse_args()

    if not args.mot and not args.cvat:
        ap.error("Cần ít nhất --mot hoặc --cvat.")

    rep = Report()
    print("Số frame in theo CVAT (bắt đầu từ 0). Trong gt.txt, frame_id = frame CVAT + 1.")
    for p in (args.mot, args.cvat):
        if p and not p.exists():
            print(f"[LỖI] Không thấy file {p}")
            return 1
    if args.mot:
        check_mot(args.mot, args.expected, rep)
    if args.cvat:
        check_cvat(args.cvat, rep)

    print("\n=== Tóm tắt ===")
    print(f"  Lỗi: {rep.errors}   |   Cảnh báo: {rep.warnings}")
    if rep.errors:
        print("  Còn [LỖI]: sửa trên CVAT, xuất lại rồi chạy lại script.")
    elif rep.warnings:
        print("  Không có lỗi định dạng. Mở CVAT xem lại từng [CẢNH BÁO]; cảnh báo đúng ý bạn thì ghi lý do vào báo cáo.")
    else:
        print("  Đạt. Dán phần tóm tắt này vào báo cáo mục 5.")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
