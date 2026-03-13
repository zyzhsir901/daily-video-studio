from __future__ import annotations

import json
from pathlib import Path
import shutil
from typing import Any
from urllib.parse import quote, urljoin, urlparse

import requests


def _post_event(base_url: str, endpoint: str, data: list[Any]) -> str:
    response = requests.post(
        f"{base_url}/gradio_api/call/{endpoint}",
        json={"data": data},
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()
    event_id = payload.get("event_id")
    if not event_id:
        raise ValueError(f"Missing event_id for endpoint {endpoint}")
    return event_id


def _wait_for_event(base_url: str, endpoint: str, event_id: str, timeout: int = 600) -> Any:
    response = requests.get(
        f"{base_url}/gradio_api/call/{endpoint}/{event_id}",
        stream=True,
        timeout=timeout,
    )
    response.raise_for_status()

    last_data: Any = None
    for line in response.iter_lines(decode_unicode=True):
        if not line or not line.startswith("data:"):
            continue
        raw = line[5:].strip()
        if not raw or raw == "null":
            continue
        try:
            last_data = json.loads(raw)
        except json.JSONDecodeError:
            last_data = raw

    if last_data is None:
        raise ValueError(f"No result returned for endpoint {endpoint}")
    return last_data


def _artifact_url(base_url: str, reference: Any) -> str | None:
    if isinstance(reference, str):
        parsed = urlparse(reference)
        if parsed.scheme in {"http", "https"}:
            return reference
        if Path(reference).exists():
            return reference
        return urljoin(f"{base_url}/", f"gradio_api/file={quote(reference)}")

    if isinstance(reference, dict):
        for key in ("url", "path", "name"):
            value = reference.get(key)
            if not value:
                continue
            resolved = _artifact_url(base_url, value)
            if resolved:
                return resolved

    if isinstance(reference, list) and reference:
        return _artifact_url(base_url, reference[0])

    return None


def _save_artifact(base_url: str, reference: Any, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    source = _artifact_url(base_url, reference)
    if not source:
        raise ValueError("Could not resolve artifact location from API response")

    parsed = urlparse(source)
    if parsed.scheme in {"http", "https"}:
        with requests.get(source, stream=True, timeout=120) as response:
            response.raise_for_status()
            with output_path.open("wb") as handle:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        handle.write(chunk)
        return output_path

    shutil.copy2(source, output_path)
    return output_path


def generate_image(
    prompt: str,
    output_path: Path,
    base_url: str,
    ratio: str,
    seed: int = 42,
    steps: int = 8,
    time_shift: int = 3,
    random_seed: bool = True,
) -> Path:
    event_id = _post_event(
        base_url,
        "generate",
        [prompt, ratio, seed, steps, time_shift, random_seed, []],
    )
    result = _wait_for_event(base_url, "generate", event_id)
    if not isinstance(result, list) or not result:
        raise ValueError("Image generation returned an unexpected payload")
    gallery = result[0]
    return _save_artifact(base_url, gallery, output_path)


def infer_video_resolution(image_path: Path, base_url: str, high_res: bool) -> tuple[int, int]:
    event_id = _post_event(
        base_url,
        "on_image_upload",
        [{"path": str(image_path), "meta": {"_type": "gradio.FileData"}}, high_res],
    )
    result = _wait_for_event(base_url, "on_image_upload", event_id)
    if not isinstance(result, list) or len(result) < 2:
        raise ValueError("Video resolution endpoint returned an unexpected payload")
    width = int(result[0])
    height = int(result[1])
    return width, height


def generate_video(
    image_path: Path,
    output_path: Path,
    prompt: str,
    base_url: str,
    duration_seconds: float,
    high_res: bool,
    seed: int = 10,
    randomize_seed: bool = True,
    enhance_prompt: bool = False,
) -> Path:
    width, height = infer_video_resolution(image_path, base_url, high_res)
    event_id = _post_event(
        base_url,
        "generate_video",
        [
            {"path": str(image_path), "meta": {"_type": "gradio.FileData"}},
            prompt,
            duration_seconds,
            enhance_prompt,
            seed,
            randomize_seed,
            height,
            width,
        ],
    )
    result = _wait_for_event(base_url, "generate_video", event_id, timeout=1800)
    if not isinstance(result, list) or not result:
        raise ValueError("Video generation returned an unexpected payload")
    video_ref = result[0]
    return _save_artifact(base_url, video_ref, output_path)
