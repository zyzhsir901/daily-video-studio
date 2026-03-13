from __future__ import annotations

from pathlib import Path


class MediaGenerationSkipped(RuntimeError):
    """Raised when media generation is not configured."""


def generate_image(
    prompt: str,
    output_path: Path,
    base_url: str,
    api_key: str,
    ratio: str,
) -> Path:
    raise MediaGenerationSkipped(
        "Image API is not configured yet. Set IMAGE_API_BASE_URL and implement this client for your provider."
    )


def generate_video(
    image_path: Path,
    output_path: Path,
    prompt: str,
    base_url: str,
    api_key: str,
    duration_seconds: float,
) -> Path:
    raise MediaGenerationSkipped(
        "Video API is not configured yet. Set VIDEO_API_BASE_URL and implement this client for your provider."
    )
