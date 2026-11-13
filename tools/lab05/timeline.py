"""Tạo timeline HTML ngoại tuyến từ file xuất Lab Ngày 5 (Python 3.9+)."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

FRAME_COUNT = 150
TEMPLATE = Path(__file__).with_name("timeline-template.html")
STATUS = re.compile(r"^\s*\[(CẢNH BÁO|LỖI)\]\s+(.*)$")
FRAME_LIST = re.compile(r"\b(?:ở|ví dụ) frame \[(-?\d+(?:,\s*-?\d+)*)\]")
FRAME_RANGE = re.compile(r"^Track -?\d+: vắng \d+ frame \(frame (-?\d+)–(-?\d+)\)")
SINGLE_FRAME = re.compile(r"^Track -?\d+ frame (-?\d+):")


def load_tracks(path: Path) -> tuple[list, str | None]:
    """Read box states from the same ZIP member convention as the checker."""
    try:
        if path.suffix.lower() == ".zip":
            with zipfile.ZipFile(path) as archive:
                member = next(
                    (name for name in archive.namelist()
                     if name.replace("\\", "/").endswith("annotations.xml")),
                    None,
                )
                if member is None:
                    return [], "Không tìm thấy annotations.xml trong file ZIP."
                with archive.open(member) as xml_file:
                    root = ET.parse(xml_file).getroot()
        else:
            root = ET.parse(path).getroot()
    except (ET.ParseError, OSError, zipfile.BadZipFile, RuntimeError) as exc:
        return [], f"Không đọc được XML: {exc}"

    tracks = []
    skipped = 0
    for track in root.findall("track"):
        boxes = track.findall("box")
        if not boxes:
            continue
        states = {}
        for box in boxes:
            try:
                frame = int(box.get("frame", ""))
            except ValueError:
                skipped += 1
                continue
            if not 0 <= frame < FRAME_COUNT:
                skipped += 1
                continue
            state = "visible"
            if box.get("outside") == "1":
                state = "outside"
            elif box.get("occluded") == "1":
                state = "occluded"
            states[frame] = (state, box.get("keyframe") == "1")

        segments = []
        keyframes = []
        for frame, (state, keyframe) in sorted(states.items()):
            if not segments or segments[-1][1] != state:
                segments.append((frame, state))
            if keyframe:
                keyframes.append(frame)
        tracks.append({
            "id": track.get("id", "?"),
            "label": track.get("label", "?"),
            "segments": segments,
            "keyframes": keyframes,
        })
    note = f"Đã bỏ qua {skipped} box có frame sai hoặc nằm ngoài 0–149." if skipped else None
    return tracks, note


def frame_links(message: str) -> list:
    """Extract explicit CVAT-frame references from the checker's warning formats."""
    span = FRAME_RANGE.search(message)
    if span:
        start, end = map(int, span.groups())
        if 0 <= start <= end < FRAME_COUNT:
            return [(start, end)]

    sample = FRAME_LIST.search(message) if message.startswith("Track ") else None
    if sample:
        frames = (int(value) for value in sample[1].split(","))
        return [(frame, frame) for frame in dict.fromkeys(frames) if 0 <= frame < FRAME_COUNT]

    single = SINGLE_FRAME.search(message)
    if single:
        frame = int(single[1])
        if 0 <= frame < FRAME_COUNT:
            return [(frame, frame)]
    return []


def checker_issues(output: str) -> list:
    source = "Checker"
    issues = []
    for line in output.splitlines():
        if line.startswith("=== File MOT 1.1:"):
            source = "MOT"
        elif line.startswith("=== File CVAT for video 1.1:"):
            source = "CVAT XML"
        match = STATUS.match(line)
        if match:
            severity, message = match.groups()
            issues.append({
                "source": source,
                "severity": severity,
                "message": message,
                "frames": frame_links(message) if source == "MOT" else [],
            })
    return issues


def run_checker(args: argparse.Namespace, checker: Path) -> tuple[str, list, str | None]:
    command = [sys.executable, str(checker), "--cvat", str(args.cvat), "--expected", str(args.expected)]
    if args.mot:
        command.extend(["--mot", str(args.mot)])
    result = subprocess.run(command, capture_output=True, encoding="utf-8", errors="replace", check=False)
    report = result.stdout.rstrip()
    if result.stderr.strip():
        report = f"{report}\n\n{result.stderr.rstrip()}".strip()
    failed = result.returncode not in (0, 1) or "=== Tóm tắt ===" not in result.stdout.splitlines()
    notice = f"Checker dừng với mã {result.returncode}. Xem kết quả chi tiết bên dưới." if failed else None
    return report, checker_issues(result.stdout), notice


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cvat", type=Path, required=True, help="CVAT for video 1.1 (.zip hoặc annotations.xml)")
    parser.add_argument("--mot", type=Path, help="MOT 1.1 (.zip hoặc gt.txt)")
    parser.add_argument("--checker", type=Path, help="Đường dẫn đến check_submission.py của lab")
    parser.add_argument("--expected", type=int, default=5, help="Số track MOT mong đợi (mặc định 5)")
    parser.add_argument("--output", type=Path, default=Path("timeline.html"), help="File HTML đích (mặc định timeline.html)")
    args = parser.parse_args()

    checker = args.checker
    if checker is None:
        candidates = (Path("src/check_submission.py"), Path(__file__).with_name("check_submission.py"))
        checker = next((path for path in candidates if path.is_file()), candidates[0])
    if not checker.is_file():
        parser.error("Không thấy check_submission.py. Hãy chạy từ gốc repo lab hoặc thêm --checker.")
    inputs = [args.cvat, checker, TEMPLATE, Path(__file__)]
    if args.mot:
        inputs.append(args.mot)
    for path in inputs:
        if not path.is_file():
            parser.error(f"Không tìm thấy file {path}")
    if args.output.resolve() in {path.resolve() for path in inputs}:
        parser.error("--output cần khác file đầu vào.")
    if args.output.suffix.lower() != ".html":
        parser.error("--output cần có đuôi .html.")
    if args.expected < 1:
        parser.error("--expected cần là số nguyên dương.")

    try:
        report, issues, checker_notice = run_checker(args, checker.resolve())
        tracks, track_notice = load_tracks(args.cvat)
        data = {
            "frameCount": FRAME_COUNT,
            "cvat": args.cvat.name,
            "mot": args.mot.name if args.mot else None,
            "tracks": tracks,
            "trackNotice": track_notice,
            "issues": issues,
            "checkerNotice": checker_notice,
            "report": report,
        }
        # Prevent filenames, labels and checker output from ending the JSON script tag.
        payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
        html = TEMPLATE.read_text(encoding="utf-8").replace("<!--TIMELINE_DATA-->", payload, 1)
        args.output.write_text(html, encoding="utf-8")
    except OSError as exc:
        parser.exit(2, f"Lỗi tạo timeline: {exc}\n")

    print(f"Đã tạo {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
