from __future__ import annotations

from datetime import datetime
import json
import os
from pathlib import Path
import shutil

from dotenv import load_dotenv

from .assembler import assemble_clips_ffmpeg
from .crew import DailyBuildingVideoCrew
from .media_clients import MediaGenerationSkipped, generate_image, generate_video
from .models import BuildConcept, VideoPackage
from .package_builder import build_video_package
from .theme_library import build_daily_concept
from .utils import ensure_dir


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _run_root(report_date: str) -> Path:
    return _project_root() / "building-video-runs" / report_date


def _runs_root() -> Path:
    return _project_root() / "building-video-runs"


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} is required")
    return value


def _save_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _save_script(path: Path, concept: BuildConcept, package: VideoPackage) -> None:
    lines = [
        f"# {package.video_title}",
        "",
        f"Date: {concept.date_key}",
        f"Seed: {concept.seed}",
        f"Building Type: {concept.building_type}",
        f"Location Style: {concept.location_style}",
        f"Visual Style: {concept.visual_style}",
        f"Tone: {concept.tone}",
        "",
        "## Hook",
        package.video_hook,
        "",
        "## Creative Direction",
        package.creative_direction,
        "",
        "## Music Direction",
        package.music_direction,
        "",
    ]
    for segment in package.segments:
        lines.extend(
            [
                f"## Segment {segment.rank}",
                f"Stage: {segment.stage_name}",
                f"Shot Goal: {segment.shot_goal}",
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


def _write_inputs(inputs_dir: Path, concept: BuildConcept) -> None:
    ensure_dir(inputs_dir)
    _save_json(inputs_dir / "build_concept.json", concept.to_dict())


def _clear_previous_outputs() -> None:
    runs_root = _runs_root()
    if runs_root.exists():
        shutil.rmtree(runs_root)
    ensure_dir(runs_root)
    (runs_root / ".gitkeep").write_text("", encoding="utf-8")


def _generate_video_package(concept: BuildConcept, segment_count: int) -> VideoPackage:
    payload = DailyBuildingVideoCrew().run(
        report_date=concept.date_key,
        seed=concept.seed,
        building_type=concept.building_type,
        location_style=concept.location_style,
        visual_style=concept.visual_style,
        tone=concept.tone,
        stage_sequence=concept.stage_sequence,
        segment_count=segment_count,
        target_duration_seconds=concept.total_duration_seconds,
    )
    return build_video_package(payload, segment_count=segment_count)


def _generate_assets(run_root: Path, package: VideoPackage) -> tuple[list[Path], list[dict]]:
    image_base_url = (os.getenv("IMAGE_API_BASE_URL") or "").rstrip("/")
    image_api_key = os.getenv("IMAGE_API_KEY") or ""
    image_ratio = os.getenv("IMAGE_RATIO") or "720x1280"
    video_base_url = (os.getenv("VIDEO_API_BASE_URL") or "").rstrip("/")
    video_api_key = os.getenv("VIDEO_API_KEY") or ""
    default_duration = float(os.getenv("VIDEO_DURATION_SECONDS") or "3.2")

    images_dir = ensure_dir(run_root / "assets" / "images")
    clips_dir = ensure_dir(run_root / "assets" / "clips")

    clips: list[Path] = []
    manifest_segments: list[dict] = []
    for segment in package.segments:
        image_path = images_dir / f"{segment.rank:02d}.png"
        clip_path = clips_dir / f"{segment.rank:02d}.mp4"
        segment_record = {
            "rank": segment.rank,
            "stage_name": segment.stage_name,
            "image_path": None,
            "clip_path": None,
            "image_status": "pending",
            "video_status": "pending",
        }

        if not image_base_url:
            segment_record["image_status"] = "skipped: IMAGE_API_BASE_URL not set"
            segment_record["video_status"] = "skipped: image generation unavailable"
            manifest_segments.append(segment_record)
            continue

        try:
            generated_image = generate_image(
                prompt=segment.image_prompt,
                output_path=image_path,
                base_url=image_base_url,
                api_key=image_api_key,
                ratio=image_ratio,
            )
            segment_record["image_path"] = str(generated_image)
            segment_record["image_status"] = "ok"
        except MediaGenerationSkipped as exc:
            segment_record["image_status"] = f"skipped: {exc}"
            segment_record["video_status"] = "skipped: image generation unavailable"
            manifest_segments.append(segment_record)
            continue
        except Exception as exc:
            segment_record["image_status"] = f"failed: {exc}"
            segment_record["video_status"] = "skipped: image generation failed"
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
                api_key=video_api_key,
                duration_seconds=segment.duration_seconds or default_duration,
            )
            clips.append(generated_clip)
            segment_record["clip_path"] = str(generated_clip)
            segment_record["video_status"] = "ok"
        except MediaGenerationSkipped as exc:
            segment_record["video_status"] = f"skipped: {exc}"
        except Exception as exc:
            segment_record["video_status"] = f"failed: {exc}"

        manifest_segments.append(segment_record)

    return clips, manifest_segments


def run_pipeline() -> Path:
    load_dotenv()
    _require_env("GEMINI_API_KEY")

    report_date = datetime.now().strftime("%Y-%m-%d")
    segment_count = int(os.getenv("BUILDING_SEGMENT_COUNT", "6"))
    concept = build_daily_concept(segment_count=segment_count)
    _clear_previous_outputs()
    run_root = _run_root(report_date)
    ensure_dir(run_root)

    _write_inputs(run_root / "inputs", concept)
    package = _generate_video_package(concept, segment_count=segment_count)

    planning_dir = ensure_dir(run_root / "planning")
    script_dir = ensure_dir(run_root / "script")
    outputs_dir = ensure_dir(run_root / "outputs")

    _save_json(planning_dir / "video_package.json", package.to_dict())
    _save_script(script_dir / "video_script.md", concept, package)

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
        "concept": concept.to_dict(),
        "selected_segments": len(package.segments),
        "video_title": package.video_title,
        "final_video_path": str(final_video_path) if final_video_path else None,
        "final_video_status": final_video_status,
        "segments": manifest_segments,
    }
    _save_json(outputs_dir / "manifest.json", manifest)
    return run_root
