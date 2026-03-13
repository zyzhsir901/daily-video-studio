from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil

from dotenv import load_dotenv

from .assembler import assemble_clips_ffmpeg
from .crew import TodayInternationalNewsCrew
from .media_clients import generate_image, generate_video
from .models import NewsItem, VideoPackage
from .news_sources import NEWS_SOURCE_URL, RSS_URL, build_digest, fetch_google_news_items
from .package_builder import build_video_package
from .utils import ensure_dir, extract_json_object


def _content_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _run_root(report_date: str) -> Path:
    return _content_root() / "runs" / report_date


def _runs_root() -> Path:
    return _content_root() / "runs"


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} is required")
    return value


def _save_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _save_script(path: Path, package: VideoPackage) -> None:
    lines = [
        f"# {package.video_title}",
        "",
        "## Hook",
        package.video_hook,
        "",
        "## Global Outlook",
        package.global_outlook,
        "",
    ]
    for segment in package.segments:
        lines.extend(
            [
                f"## Segment {segment.rank}",
                f"Headline: {segment.headline}",
                f"Source: {segment.source}",
                f"Link: {segment.source_link}",
                f"Why It Matters: {segment.why_it_matters}",
                f"Narration: {segment.narration}",
                f"On Screen Text: {segment.on_screen_text}",
                f"Image Prompt: {segment.image_prompt}",
                f"Video Prompt: {segment.video_prompt}",
                f"Duration Seconds: {segment.duration_seconds}",
                "",
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def _clear_previous_outputs() -> None:
    runs_root = _runs_root()
    if runs_root.exists():
        shutil.rmtree(runs_root)
    ensure_dir(runs_root)
    (runs_root / ".gitkeep").write_text("", encoding="utf-8")


def _write_inputs(inputs_dir: Path, items: list[NewsItem], digest: str) -> None:
    ensure_dir(inputs_dir)
    _save_json(inputs_dir / "news_candidates.json", {"items": [item.to_dict() for item in items]})
    (inputs_dir / "news_digest.txt").write_text(digest, encoding="utf-8")


def _generate_video_package(report_date: str, digest: str, max_news: int) -> VideoPackage:
    result = TodayInternationalNewsCrew().crew().kickoff(
        inputs={
            "report_date": report_date,
            "news_digest": digest,
            "max_news": max_news,
        }
    )
    payload = extract_json_object(str(result))
    return build_video_package(payload, max_news=max_news)


def _generate_assets(run_root: Path, package: VideoPackage) -> tuple[list[Path], list[dict]]:
    image_base_url = (os.getenv("IMAGE_API_BASE_URL") or "https://tongyi-mai-z-image-turbo.hf.space").rstrip("/")
    image_ratio = os.getenv("IMAGE_RATIO") or "1024x1024 ( 1:1 )"
    video_base_url = (os.getenv("VIDEO_API_BASE_URL") or "").rstrip("/")
    video_high_res = (os.getenv("VIDEO_HIGH_RES") or "false").lower() == "true"
    default_duration = float(os.getenv("VIDEO_DURATION_SECONDS") or "3.0")

    images_dir = ensure_dir(run_root / "assets" / "images")
    clips_dir = ensure_dir(run_root / "assets" / "clips")

    clips: list[Path] = []
    manifest_segments: list[dict] = []
    for segment in package.segments:
        image_path = images_dir / f"{segment.rank:02d}.png"
        clip_path = clips_dir / f"{segment.rank:02d}.mp4"
        segment_record = {
            "rank": segment.rank,
            "headline": segment.headline,
            "image_path": None,
            "clip_path": None,
            "image_status": "pending",
            "video_status": "pending",
        }

        try:
            generated_image = generate_image(
                prompt=segment.image_prompt,
                output_path=image_path,
                base_url=image_base_url,
                ratio=image_ratio,
            )
            segment_record["image_path"] = str(generated_image)
            segment_record["image_status"] = "ok"
        except Exception as exc:
            segment_record["image_status"] = f"failed: {exc}"
            segment_record["video_status"] = "skipped"
            manifest_segments.append(segment_record)
            continue

        if not video_base_url:
            segment_record["video_status"] = "skipped: VIDEO_API_BASE_URL not set"
            manifest_segments.append(segment_record)
            continue

        try:
            generated_clip = generate_video(
                image_path=image_path,
                output_path=clip_path,
                prompt=segment.video_prompt,
                base_url=video_base_url,
                duration_seconds=segment.duration_seconds or default_duration,
                high_res=video_high_res,
            )
            clips.append(generated_clip)
            segment_record["clip_path"] = str(generated_clip)
            segment_record["video_status"] = "ok"
        except Exception as exc:
            segment_record["video_status"] = f"failed: {exc}"

        manifest_segments.append(segment_record)

    return clips, manifest_segments


def run_pipeline() -> Path:
    load_dotenv()
    _require_env("OPENAI_API_KEY")

    report_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    max_news = int(os.getenv("PIPELINE_MAX_NEWS", "8"))
    _clear_previous_outputs()
    run_root = _run_root(report_date)
    ensure_dir(run_root)

    news_items = fetch_google_news_items(limit=max_news * 4)
    news_digest = build_digest(news_items, max_items=max_news * 3)
    _write_inputs(run_root / "inputs", news_items, news_digest)

    package = _generate_video_package(report_date, news_digest, max_news=max_news)
    planning_dir = ensure_dir(run_root / "planning")
    script_dir = ensure_dir(run_root / "script")
    outputs_dir = ensure_dir(run_root / "outputs")

    _save_json(planning_dir / "video_package.json", package.to_dict())
    _save_script(script_dir / "video_script.md", package)

    clips, manifest_segments = _generate_assets(run_root, package)

    final_video_path = None
    final_video_status = "skipped"
    if clips:
        try:
            final_video_path = assemble_clips_ffmpeg(clips, outputs_dir / "final_video.mp4")
            final_video_status = "ok"
        except Exception as exc:
            final_video_status = f"failed: {exc}"

    manifest = {
        "report_date": report_date,
        "rss_url": RSS_URL,
        "topic_url": NEWS_SOURCE_URL,
        "selected_segments": len(package.segments),
        "video_title": package.video_title,
        "final_video_path": str(final_video_path) if final_video_path else None,
        "final_video_status": final_video_status,
        "segments": manifest_segments,
    }
    _save_json(outputs_dir / "manifest.json", manifest)
    return run_root
