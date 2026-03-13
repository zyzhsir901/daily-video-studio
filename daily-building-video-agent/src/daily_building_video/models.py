from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class BuildConcept:
    date_key: str
    seed: int
    building_type: str
    location_style: str
    visual_style: str
    tone: str
    stage_sequence: list[str]
    total_duration_seconds: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class VideoSegment:
    rank: int
    stage_name: str
    shot_goal: str
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
    creative_direction: str
    music_direction: str
    segments: list[VideoSegment]

    def to_dict(self) -> dict:
        return {
            "video_title": self.video_title,
            "video_hook": self.video_hook,
            "creative_direction": self.creative_direction,
            "music_direction": self.music_direction,
            "segments": [segment.to_dict() for segment in self.segments],
        }
