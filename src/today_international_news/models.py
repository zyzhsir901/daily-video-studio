from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class NewsItem:
    source: str
    title: str
    link: str
    published_at: str
    summary: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class VideoSegment:
    rank: int
    headline: str
    source: str
    source_link: str
    why_it_matters: str
    narration: str
    on_screen_text: str
    image_prompt: str
    video_prompt: str
    duration_seconds: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class VideoPackage:
    video_title: str
    video_hook: str
    global_outlook: str
    segments: list[VideoSegment]

    def to_dict(self) -> dict:
        return {
            "video_title": self.video_title,
            "video_hook": self.video_hook,
            "global_outlook": self.global_outlook,
            "segments": [segment.to_dict() for segment in self.segments],
        }

