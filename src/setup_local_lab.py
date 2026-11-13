"""Assign a MOT17-09 variant and prepare a blank job on local CVAT."""

import argparse
from getpass import getpass
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
from urllib.parse import urlsplit
from zipfile import BadZipFile, ZipFile


ROOT = Path(__file__).resolve().parents[1]
LOCAL_DATA = ROOT / ".lab-local"
MOT_URL = "https://motchallenge.net/data/MOT17Det.zip"
FRAME_NAMES = tuple(f"{frame:06d}.jpg" for frame in range(1, 151))
FRAMES_SHA256 = "0859619ba926ee746050509390c1f4708ab2d0cf86366253df9d20a2c6fbcaf1"


def student_id(value):
    value = value.strip().upper()
    if not re.fullmatch(r"[A-Z0-9][A-Z0-9-]{0,63}", value):
        raise argparse.ArgumentTypeError("Nhập MSSV bằng chữ cái, chữ số hoặc dấu gạch ngang.")
    return value


def variant_for(mssv):
    digest = sha256(student_id(mssv).encode("ascii")).digest()
    return "ABC"[int.from_bytes(digest, "big") % 3]


def local_server(value):
    try:
        url = urlsplit(value)
        valid_port = url.port is None or url.port > 0
    except ValueError as error:
        raise argparse.ArgumentTypeError("Địa chỉ CVAT không hợp lệ.") from error

    if (
        url.scheme not in ("http", "https")
        or url.hostname not in ("localhost", "127.0.0.1", "::1")
        or not valid_port
        or url.username is not None
        or url.password is not None
        or url.path not in ("", "/")
        or url.query
        or url.fragment
    ):
        raise argparse.ArgumentTypeError("Dùng địa chỉ CVAT local, ví dụ http://localhost:8080.")
    return value.rstrip("/")


def verify_frames(directory):
    frames = [directory / name for name in FRAME_NAMES]
    digest = sha256()
    for frame in frames:
        if not frame.is_file():
            raise ValueError(f"Thiếu ảnh {frame}. Cần ảnh 000001.jpg–000150.jpg của MOT17-09.")
        digest.update(frame.read_bytes())
    if digest.hexdigest() != FRAMES_SHA256:
        raise ValueError(f"Ảnh trong {directory} không khớp MOT17-09 gốc. Kiểm tra lại thư mục ảnh.")
    return frames


def prepare_frames(directory):
    if directory is not None:
        return verify_frames(directory)

    destination = LOCAL_DATA / "mot17-09"
    if destination.exists():
        return verify_frames(destination)

    import fsspec
    from aiohttp import ClientError

    print("Đang tải 150 ảnh MOT17-09 từ MOTChallenge…", flush=True)
    with TemporaryDirectory(dir=LOCAL_DATA) as temporary:
        staged = Path(temporary) / destination.name
        staged.mkdir()
        try:
            with fsspec.open(MOT_URL, "rb") as remote, ZipFile(remote) as archive:
                for name in FRAME_NAMES:
                    (staged / name).write_bytes(archive.read(f"train/MOT17-09/img1/{name}"))
        except (ClientError, OSError, BadZipFile, KeyError) as error:
            raise ValueError(
                "Không tải được ảnh MOTChallenge. Thử lại hoặc tải ZIP và dùng --frames-dir."
            ) from error
        verify_frames(staged)
        try:
            staged.rename(destination)
        except OSError:
            if not destination.is_dir():
                raise
    return verify_frames(destination)


def make_reference(variant, config, frames):
    from PIL import Image, ImageDraw

    width, height = 960, 540
    targets = config["variants"][variant]
    sheet = Image.new("RGB", (width, (height + 38) * len(targets)), "#16232c")
    headings = ImageDraw.Draw(sheet)
    for index, target_id in enumerate(targets, start=1):
        reference = config["targets"][str(target_id)]
        image_number = reference["image"]
        x, y = reference["point"]
        with Image.open(frames[image_number - 1]) as source:
            image = source.resize((width, height), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(image)
        x, y = x // 2, y // 2
        draw.ellipse((x - 11, y - 11, x + 11, y + 11), outline="black", width=5)
        draw.ellipse((x - 11, y - 11, x + 11, y + 11), outline="yellow", width=2)
        top = (index - 1) * (height + 38)
        sheet.paste(image, (0, top + 38))
        headings.text(
            (14, top + 11),
            f"De {variant}  |  P{index}  |  CVAT frame {image_number - 1}",
            fill="white",
        )
    path = LOCAL_DATA / f"de-{variant}-P1-P5.jpg"
    sheet.save(path, quality=90)
    return path


def open_or_create_job(client, task_name, frames):
    from cvat_sdk.api_client import models

    matches = [task for task in client.tasks.list(search=task_name) if task.name == task_name]
    if len(matches) > 1:
        raise ValueError(f"Có nhiều task tên {task_name}. Đổi tên task trùng trong CVAT rồi chạy lại.")

    if matches:
        task = matches[0]
        print(f"Tìm thấy task #{task.id}, đang kiểm tra dữ liệu đã có…", flush=True)
    else:
        print("Đang tạo task và tải ảnh vào CVAT local…", flush=True)
        task = client.tasks.create_from_data(
            spec=models.TaskWriteRequest(
                name=task_name,
                labels=[models.PatchedLabelRequest(name="person", type="rectangle")],
                segment_size=len(FRAME_NAMES),
            ),
            resources=frames,
            data_params={"sorting_method": "lexicographical"},
        )

    jobs = task.get_jobs()
    if not jobs:
        raise ValueError(
            f"Task #{task.id} chưa có job. Đợi CVAT xử lý xong trong Requests rồi chạy lại. "
            "Nếu request đã báo lỗi, đổi tên task đó trước khi thử lại."
        )

    meta = task.get_meta()
    expected_job = len(jobs) == 1 and (jobs[0].start_frame, jobs[0].stop_frame) == (0, 149)
    expected_labels = [label.name for label in task.get_labels()] == ["person"]
    expected_frames = tuple(Path(frame.name).name for frame in meta.frames) == FRAME_NAMES
    if not (expected_job and expected_labels and expected_frames):
        raise ValueError(
            f"Task #{task.id} có dữ liệu khác hướng dẫn. Đổi tên task đó trong CVAT rồi chạy lại."
        )
    return task.id, jobs[0].id


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mssv", type=student_id, help="MSSV. Bỏ qua để nhập khi chạy.")
    parser.add_argument("--server", default="http://localhost:8080", type=local_server)
    parser.add_argument("--frames-dir", type=Path, help="Thư mục có 150 ảnh MOT17-09 đã tải.")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--assignment-only", action="store_true", help="Chỉ xem mã đề.")
    modes.add_argument("--prepare-only", action="store_true", help="Tải ảnh và tạo bảng nhận diện.")
    args = parser.parse_args()

    try:
        mssv = args.mssv or student_id(input("Nhập MSSV: "))
        variant = variant_for(mssv)
        task_name = f"DAY05-MOT17-09-{variant}-{mssv}"
        print(f"Đề {variant} | Task: {task_name}", flush=True)
        if args.assignment_only:
            return 0

        config = json.loads((ROOT / "src" / "lab_variants.json").read_text(encoding="utf-8"))
        LOCAL_DATA.mkdir(exist_ok=True)
        frames = prepare_frames(args.frames_dir)
        reference = make_reference(variant, config, frames)
        print(f"Ảnh nhận diện P1–P5: {reference}\nThư mục ảnh gốc: {frames[0].parent}", flush=True)
        if args.prepare_only:
            return 0

        from cvat_sdk import make_client
        from cvat_sdk.api_client.exceptions import ApiException
        from cvat_sdk.core.exceptions import CvatSdkException
        from urllib3.exceptions import HTTPError

        username = input("Tên đăng nhập CVAT local: ").strip()
        password = getpass("Mật khẩu CVAT local: ")
        try:
            with make_client(host=args.server, credentials=(username, password)) as client:
                task_id, job_id = open_or_create_job(client, task_name, frames)
        except ApiException as error:
            if error.status in (400, 401, 403):
                raise ValueError(
                    f"CVAT trả về HTTP {error.status}. Kiểm tra đăng nhập và quyền tạo task."
                ) from error
            raise ValueError(f"CVAT trả về HTTP {error.status}. Mở CVAT và kiểm tra mục Requests.") from error
        except (CvatSdkException, HTTPError) as error:
            raise ValueError(
                f"Không hoàn tất trên CVAT tại {args.server} ({type(error).__name__}). "
                "Kiểm tra CVAT đang chạy và xem mục Requests trước khi thử lại."
            ) from error
        print(f"Task: {args.server}/tasks/{task_id}")
        print(f"Job:  {args.server}/tasks/{task_id}/jobs/{job_id}")
    except (argparse.ArgumentTypeError, OSError, ValueError, ImportError, EOFError) as error:
        print(f"Lỗi: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
