from __future__ import annotations

from .models import VideoPackage, VideoSegment


def build_video_package(payload: dict, segment_count: int) -> VideoPackage:
    raw_segments = payload.get("segments") or []
    if not isinstance(raw_segments, list) or not raw_segments:
        raise ValueError("Model output does not include usable segments")

    segments: list[VideoSegment] = []
    for index, raw_segment in enumerate(raw_segments[:segment_count], start=1):
        segments.append(
            VideoSegment(
                rank=index,
                stage_name=str(raw_segment.get("stage_name", "")).strip(),
                shot_goal=str(raw_segment.get("shot_goal", "")).strip(),
                narration=str(raw_segment.get("narration", "")).strip(),
                on_screen_text=str(raw_segment.get("on_screen_text", "")).strip(),
                image_prompt=str(raw_segment.get("image_prompt", "")).strip(),
                video_prompt=str(raw_segment.get("video_prompt", "")).strip(),
                duration_seconds=float(raw_segment.get("duration_seconds", 3.2) or 3.2),
            )
        )

    if not segments:
        raise ValueError("No valid video segments were produced")

    return VideoPackage(
        video_title=str(payload.get("video_title", "AI Building Process")).strip(),
        video_hook=str(payload.get("video_hook", "")).strip(),
        creative_direction=str(payload.get("creative_direction", "")).strip(),
        music_direction=str(payload.get("music_direction", "")).strip(),
        segments=segments,
    )
