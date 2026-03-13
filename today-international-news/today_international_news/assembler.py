from __future__ import annotations

from pathlib import Path
import subprocess


def _escape_drawtext(value: str) -> str:
    escaped = value.replace("\\", "\\\\")
    escaped = escaped.replace(":", "\\:")
    escaped = escaped.replace("'", r"\'")
    escaped = escaped.replace("%", r"\%")
    escaped = escaped.replace(",", r"\,")
    escaped = escaped.replace("[", r"\[")
    escaped = escaped.replace("]", r"\]")
    return escaped


def _run_ffmpeg(command: list[str]) -> None:
    subprocess.run(command, check=True)


def create_title_card(
    output_path: Path,
    title: str,
    subtitle: str,
    width: int,
    height: int,
    duration_seconds: float = 2.5,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    title_text = _escape_drawtext(title)
    subtitle_text = _escape_drawtext(subtitle)
    filter_chain = (
        f"drawtext=text='{title_text}':fontcolor=white:fontsize={max(28, width // 17)}:"
        f"x=(w-text_w)/2:y=(h*0.32)-text_h:box=1:boxcolor=black@0.45:boxborderw=24,"
        f"drawtext=text='{subtitle_text}':fontcolor=white:fontsize={max(18, width // 28)}:"
        f"x=(w-text_w)/2:y=h*0.60:box=1:boxcolor=black@0.35:boxborderw=18"
    )
    command = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-f",
        "lavfi",
        "-i",
        f"color=c=#101820:s={width}x{height}:d={duration_seconds}",
        "-vf",
        filter_chain,
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-an",
        str(output_path),
    ]
    _run_ffmpeg(command)
    return output_path


def burn_subtitles(
    input_clip: Path,
    output_path: Path,
    headline: str,
    subtitle: str,
    width: int,
    height: int,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    headline_text = _escape_drawtext(headline)
    subtitle_text = _escape_drawtext(subtitle)
    filter_chain = (
        f"scale={width}:{height},"
        f"drawtext=text='{headline_text}':fontcolor=white:fontsize={max(24, width // 21)}:"
        f"x=(w-text_w)/2:y=h*0.08:box=1:boxcolor=black@0.45:boxborderw=18,"
        f"drawtext=text='{subtitle_text}':fontcolor=white:fontsize={max(18, width // 28)}:"
        f"x=(w-text_w)/2:y=h*0.82:box=1:boxcolor=black@0.55:boxborderw=20"
    )
    command = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-i",
        str(input_clip),
        "-vf",
        filter_chain,
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-an",
        str(output_path),
    ]
    _run_ffmpeg(command)
    return output_path


def assemble_clips_ffmpeg(clips: list[Path], output_path: Path) -> Path:
    if not clips:
        raise ValueError("No clips available for assembly")

    concat_file = output_path.parent / "concat.txt"
    concat_lines = [f"file '{clip.resolve().as_posix()}'" for clip in clips]
    concat_file.write_text("\n".join(concat_lines), encoding="utf-8")

    command = [
        "ffmpeg",
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
    _run_ffmpeg(command)
    return output_path
