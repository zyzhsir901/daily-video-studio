from __future__ import annotations

from .models import VideoPackage, VideoSegment


def build_video_package(payload: dict, max_news: int) -> VideoPackage:
    raw_segments = payload.get("segments") or []
    if not isinstance(raw_segments, list) or not raw_segments:
        raise ValueError("Model output does not include usable segments")

    segments: list[VideoSegment] = []
    for index, raw_segment in enumerate(raw_segments[:max_news], start=1):
        segments.append(
            VideoSegment(
                rank=index,
                headline=str(raw_segment.get("headline", "")).strip(),
                source=str(raw_segment.get("source", "")).strip(),
                source_link=str(raw_segment.get("source_link", "")).strip(),
                why_it_matters=str(raw_segment.get("why_it_matters", "")).strip(),
                narration=str(raw_segment.get("narration", "")).strip(),
                on_screen_text=str(raw_segment.get("on_screen_text", "")).strip(),
                image_prompt=str(raw_segment.get("image_prompt", "")).strip(),
                video_prompt=str(raw_segment.get("video_prompt", "")).strip(),
                duration_seconds=float(raw_segment.get("duration_seconds", 3.0) or 3.0),
            )
        )

    if not segments:
        raise ValueError("No valid video segments were produced")

    return VideoPackage(
        video_title=str(payload.get("video_title", "Global International News")).strip(),
        video_hook=str(payload.get("video_hook", "")).strip(),
        global_outlook=str(payload.get("global_outlook", "")).strip(),
        segments=segments,
    )

