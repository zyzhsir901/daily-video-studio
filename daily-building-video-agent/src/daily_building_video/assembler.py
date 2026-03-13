from __future__ import annotations

from pathlib import Path
import shutil
import subprocess


def assemble_clips_ffmpeg(clips: list[Path], output_path: Path) -> Path:
    if not clips:
        raise ValueError("No clips available for assembly")

    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        raise RuntimeError("ffmpeg is not installed or not in PATH")

    concat_file = output_path.parent / "concat.txt"
    concat_lines = [f"file '{clip.resolve().as_posix()}'" for clip in clips]
    concat_file.write_text("\n".join(concat_lines), encoding="utf-8")

    command = [
        ffmpeg_path,
        "-y",
        "-hide_banner",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_file),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-an",
        str(output_path),
    ]
    subprocess.run(command, check=True)
    return output_path
