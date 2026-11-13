#!/usr/bin/env python3
"""Lab 05 offline peer comparison for CVAT box-track exports (Python 3.10+)."""

import argparse
import csv
import io
import math
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from bisect import bisect_right
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cache
from pathlib import Path, PurePosixPath

Coordinates = tuple[float, float, float, float]
MAX_BOXES = 12  # Exact assignment is for small Lab 05 scenes.


@dataclass(frozen=True)
class Box:
    track: str
    label: str | None
    coordinates: Coordinates
    occluded: bool | None = None


def coordinates(x1, y1, x2, y2):
    if not all(math.isfinite(value) for value in (x1, y1, x2, y2)):
        raise ValueError("box coordinates must be finite")
    area = (x2 - x1) * (y2 - y1)
    if x1 >= x2 or y1 >= y2 or not math.isfinite(area) or area == 0:
        raise ValueError("box must have positive, finite area")
    return x1, y1, x2, y2


def cvat_flag(element, name):
    value = element.get(name, "0")
    if value not in {"0", "1"}:
        raise ValueError(f"expected {name}=0 or 1")
    return value == "1"


def read_cvat(payload, frames):
    root = ET.fromstring(payload)
    if root.tag != "annotations" or root.find("image") is not None:
        raise ValueError("expected a CVAT for video XML export")
    if root.find("meta/project") is not None:
        raise ValueError("export a single CVAT task or job")
    meta = root.find("meta/job")
    if meta is None:
        meta = root.find("meta/task")
    if meta is not None:
        if meta.findtext("start_frame", "0") != "0" or meta.findtext("frame_filter"):
            raise ValueError("use a zero-start, unfiltered clip")
        stop = meta.findtext("stop_frame")
        if stop is not None and frames[-1] > int(stop):
            raise ValueError(f"requested frame exceeds XML stop_frame {stop}")

    by_frame = defaultdict(list)
    track_ids = set()
    for track in root.findall("track"):
        track_id = str(int(track.attrib["id"]))
        if track_id in track_ids:
            raise ValueError(f"duplicate XML track {track_id}")
        track_ids.add(track_id)
        label = track.attrib["label"]
        points = {}
        for shape in track:
            if shape.tag != "box" or float(shape.get("rotation", "0")) != 0:
                raise ValueError(f"track {track_id}: only axis-aligned box tracks are supported")
            frame = int(shape.attrib["frame"])
            if frame < 0 or frame in points:
                raise ValueError(f"track {track_id}: invalid or duplicate frame {frame}")
            coords = coordinates(*(float(shape.attrib[key]) for key in ("xtl", "ytl", "xbr", "ybr")))
            box = Box(track_id, label, coords, cvat_flag(shape, "occluded"))
            points[frame] = (box, cvat_flag(shape, "outside"))
        if not points:
            raise ValueError(f"track {track_id}: no box rows")

        anchors = sorted(points)
        for frame in frames:
            position = bisect_right(anchors, frame)
            if position == 0:
                continue
            left_frame = anchors[position - 1]
            left, outside = points[left_frame]
            if outside:
                continue
            if left_frame == frame:
                by_frame[frame].append(left)
            elif position < len(anchors):
                right_frame = anchors[position]
                right, _ = points[right_frame]
                fraction = (frame - left_frame) / (right_frame - left_frame)
                coords = tuple(
                    start * (1 - fraction) + end * fraction
                    for start, end in zip(left.coordinates, right.coordinates)
                )
                by_frame[frame].append(Box(track_id, label, coords, left.occluded))
            else:
                raise ValueError(
                    f"track {track_id}: frame {frame} follows its last visible XML row "
                    f"({left_frame}); use a full CVAT export or narrow the review window"
                )
    return by_frame


def read_mot(payload, labels_payload):
    # CVAT MOT 1.1 annotation rows, not tracker prediction rows.
    labels = labels_payload.decode("utf-8-sig").splitlines() if labels_payload else []
    by_frame = defaultdict(list)
    seen = set()
    ignored = 0
    reader = csv.reader(io.StringIO(payload.decode("utf-8-sig"), newline=""))
    for row in reader:
        if not row or not any(field.strip() for field in row) or row[0].lstrip().startswith("#"):
            continue
        try:
            frame, track_id = (int(field) for field in row[:2])
            x, y, width, height = map(float, row[2:6])
            active, class_id = (int(field) for field in row[6:8])
            if frame < 1 or track_id < 0 or class_id < 1 or active not in {0, 1}:
                raise ValueError
            if len(row) < 9:
                raise ValueError
            if not active:
                ignored += 1
                continue
            if (frame, track_id) in seen:
                raise ValueError
            seen.add((frame, track_id))
            label = None
            if labels:
                label = labels[class_id - 1].strip()
                if not label:
                    raise ValueError
            by_frame[frame - 1].append(
                Box(str(track_id), label, coordinates(x, y, x + width, y + height))
            )
        except (ValueError, IndexError) as error:
            raise ValueError(
                f"MOT row {reader.line_num}: expected a valid, unique CVAT MOT 1.1 annotation row"
            ) from error
    notes = ["MOT frame numbers converted to zero-based; MOT occluded status is unavailable."]
    if not labels:
        notes.append("No MOT labels.txt; label comparison is unavailable for this file.")
    if ignored:
        notes.append(f"Excluded {ignored} ignored MOT rows across the export.")
    return by_frame, notes


def read_export(path, frames):
    try:
        if path.suffix.lower() == ".xml":
            return read_cvat(path.read_bytes(), frames), []
        if path.suffix.lower() == ".txt":
            labels = path.with_name("labels.txt")
            return read_mot(path.read_bytes(), labels.read_bytes() if labels.exists() else None)
        if path.suffix.lower() == ".zip":
            with zipfile.ZipFile(path) as archive:
                entries = [
                    name for name in archive.namelist()
                    if PurePosixPath(name).name in {"annotations.xml", "gt.txt"}
                ]
                if len(entries) != 1:
                    raise ValueError("ZIP must contain one annotations.xml or one gt.txt")
                entry = entries[0]
                payload = archive.read(entry)
                if entry.endswith(".xml"):
                    return read_cvat(payload, frames), []
                labels = str(PurePosixPath(entry).with_name("labels.txt"))
                label_payload = archive.read(labels) if labels in archive.namelist() else None
                return read_mot(payload, label_payload)
        raise ValueError("expected .xml, .txt, or .zip")
    except (OSError, ValueError, KeyError, ET.ParseError, zipfile.BadZipFile) as error:
        raise ValueError(f"{path}: {error}") from error


def iou(a, b):
    """Intersection area divided by union area for axis-aligned boxes."""
    ax1, ay1, ax2, ay2 = a.coordinates
    bx1, by1, bx2, by2 = b.coordinates
    width = max(0.0, min(ax2, bx2) - max(ax1, bx1))
    height = max(0.0, min(ay2, by2) - max(ay1, by1))
    intersection = width * height
    union = (ax2 - ax1) * (ay2 - ay1) + (bx2 - bx1) * (by2 - by1) - intersection
    return intersection / union


def assign(left, right, minimum):
    """Choose most pairs first, then maximize total IoU over those pairs."""
    if max(len(left), len(right)) > MAX_BOXES:
        raise ValueError(f"comparison supports at most {MAX_BOXES} boxes per side per frame")
    overlaps = [[iou(a, b) for b in right] for a in left]
    choices = [[j for j, score in enumerate(row) if score >= minimum] for row in overlaps]
    right_choices = Counter(j for options in choices for j in options)

    @cache
    def best(i, used):
        if i == len(left):
            return (0, 0.0), ()
        best_score, best_pairs = best(i + 1, used)
        for j in choices[i]:
            bit = 1 << j
            if used & bit:
                continue
            (count, total), pairs = best(i + 1, used | bit)
            score = count + 1, total + overlaps[i][j]
            if score > best_score:
                best_score, best_pairs = score, ((i, j),) + pairs
        return best_score, best_pairs

    _, pairs = best(0, 0)
    return [
        (i, j, overlaps[i][j], len(choices[i]) > 1 or right_choices[j] > 1)
        for i, j in pairs
    ]


def location(box):
    return "(" + ", ".join(f"{value:.1f}" for value in box.coordinates) + ")"


def compare(a_frames, b_frames, frames, minimum, review_at):
    previous_pairs = {}
    previous_frame = None
    for frame in frames:
        left = sorted(a_frames.get(frame, ()), key=lambda box: box.track)
        right = sorted(b_frames.get(frame, ()), key=lambda box: box.track)
        matches = assign(left, right, minimum)
        print(f"Frame {frame} (MOT {frame + 1}) | A {len(left)} / B {len(right)}")
        if not left and not right:
            print("  no boxes in either export")
        current_pairs = {}
        for i, j, score, ambiguous in matches:
            a, b = left[i], right[j]
            reasons = []
            if score < review_at:
                reasons.append("review box fit")
            if a.label is not None and b.label is not None and a.label != b.label:
                reasons.append(f"label differs ({a.label} / {b.label})")
            if a.occluded is not None and b.occluded is not None and a.occluded != b.occluded:
                reasons.append("occluded differs")
            if ambiguous:
                reasons.append("multiple overlap candidates")
            elif score >= review_at and not (
                a.label is not None and b.label is not None and a.label != b.label
            ):
                current_pairs[a.track] = b.track

            suffix = f" | {', '.join(reasons)}" if reasons else ""
            print(f"  A {a.track} ↔ B {b.track} | IoU {score:.3f}{suffix}")
            if reasons:
                print(f"    A {location(a)} | B {location(b)}")
        for side, boxes, paired in (
            ("A", left, {i for i, _, _, _ in matches}),
            ("B", right, {j for _, j, _, _ in matches}),
        ):
            for index, box in enumerate(boxes):
                if index not in paired:
                    label = box.label or "label unavailable"
                    print(f"  unmatched {side} {box.track} ({label}) at {location(box)}")

        if previous_frame == frame - 1:
            previous_a = {b: a for a, b in previous_pairs.items()}
            for a, b in current_pairs.items():
                if a in previous_pairs and previous_pairs[a] != b:
                    print(f"  review pair change: A {a} ↔ B {previous_pairs[a]} → B {b}")
                if b in previous_a and previous_a[b] != a:
                    print(f"  review pair change: B {b} ↔ A {previous_a[b]} → A {a}")
        previous_pairs = current_pairs
        previous_frame = frame


def selected_frames(spec):
    frames = set()
    for item in spec.split(","):
        match = re.fullmatch(r"\s*([0-9]+)(?:-([0-9]+))?\s*", item)
        if not match:
            raise ValueError("use frame numbers and ranges such as 0,24-30,149")
        start = int(match[1])
        stop = int(match[2] or match[1])
        if stop < start or stop - start > 999:
            raise ValueError("each range must be ascending and contain at most 1,000 frames")
        frames.update(range(start, stop + 1))
    if len(frames) > 1000:
        raise ValueError("select at most 1,000 frames")
    return sorted(frames)


DEMO_A = b"""<annotations><version>1.1</version>
<meta><job><start_frame>0</start_frame><stop_frame>2</stop_frame></job></meta>
<track id="4" label="person">
  <box frame="0" xtl="10" ytl="10" xbr="30" ybr="50"/>
  <box frame="2" xtl="14" ytl="10" xbr="34" ybr="50"/>
</track>
<track id="8" label="person">
  <box frame="0" xtl="65" ytl="10" xbr="85" ybr="50"/>
  <box frame="1" xtl="65" ytl="10" xbr="85" ybr="50" outside="1"/>
</track></annotations>"""

DEMO_B = b"""1,70,10,10,20,40,1,1,1
1,90,71,10,20,40,1,1,1
2,70,12,10,20,40,1,1,1
2,90,71,10,20,40,1,1,1
3,71,14,10,20,40,1,1,1
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exports", nargs="*", type=Path, metavar="EXPORT")
    parser.add_argument("--demo", action="store_true", help="compare built-in synthetic exports")
    parser.add_argument("--frames", help="zero-based list or ranges, e.g. 0,24-30,149")
    parser.add_argument("--min-iou", type=float, default=0.50, help="pairing floor (default 0.50)")
    parser.add_argument("--review-iou", type=float, default=0.80, help="flag box fit below this (default 0.80)")
    args = parser.parse_args()
    if args.demo and args.exports:
        parser.error("--demo takes no export paths")
    if not args.demo and (len(args.exports) != 2 or not args.frames):
        parser.error("give two exports and --frames, or use --demo")
    if not 0 < args.min_iou <= args.review_iou <= 1:
        parser.error("require 0 < --min-iou <= --review-iou <= 1")

    try:
        frames = selected_frames(args.frames or "0-2")
        if args.demo:
            sides = [(read_cvat(DEMO_A, frames), []), read_mot(DEMO_B, b"person\n")]
            names = ("synthetic CVAT XML", "synthetic MOT")
        else:
            sides = [read_export(path, frames) for path in args.exports]
            names = tuple(path.name for path in args.exports)

        print("Peer review aid | verify the same clip, frame origin and annotation scope.")
        print("Track IDs are local to each export. Locations are (left, top, right, bottom) in pixels.")
        print("Use frame findings for manual review. Peer agreement does not establish correctness.")
        print(f"Pair at IoU ≥ {args.min_iou:g} | review box fit below {args.review_iou:g}.")
        for side, name, (_, notes) in zip(("A", "B"), names, sides):
            print(f"{side}: {name}")
            for note in notes:
                print(f"  {note}")
        compare(sides[0][0], sides[1][0], frames, args.min_iou, args.review_iou)
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
