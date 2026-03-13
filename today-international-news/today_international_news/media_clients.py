from __future__ import annotations

import json
from pathlib import Path
import shutil
import time
from typing import Any
from urllib.parse import quote, urljoin, urlparse

import requests


def _preview(value: Any, limit: int = 500) -> str:
    text = json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value
    return text[:limit]


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
    started_at = time.monotonic()
    last_data: Any = None
    raw_lines: list[str] = []
    heartbeat_every_seconds = 30
    read_timeout_seconds = 45
    next_heartbeat_at = started_at + heartbeat_every_seconds

    while time.monotonic() - started_at < timeout and last_data is None:
        elapsed = int(time.monotonic() - started_at)
        print(
            f"Polling {endpoint} event {event_id}... elapsed={elapsed}s",
            flush=True,
        )
        try:
            with requests.get(
                f"{base_url}/gradio_api/call/{endpoint}/{event_id}",
                stream=True,
                timeout=(30, read_timeout_seconds),
            ) as response:
                response.raise_for_status()
                for line in response.iter_lines(decode_unicode=True):
                    if line is None:
                        continue
                    raw_lines.append(line)
                    if time.monotonic() >= next_heartbeat_at:
                        elapsed = int(time.monotonic() - started_at)
                        print(
                            f"Still waiting for {endpoint} event {event_id}... elapsed={elapsed}s",
                            flush=True,
                        )
                        next_heartbeat_at = time.monotonic() + heartbeat_every_seconds
                    if not line or not line.startswith("data:"):
                        continue
                    raw = line[5:].strip()
                    if not raw or raw == "null":
                        continue
                    try:
                        last_data = json.loads(raw)
                    except json.JSONDecodeError:
                        last_data = raw
                    if last_data is not None:
                        break
        except requests.ReadTimeout:
            elapsed = int(time.monotonic() - started_at)
            print(
                f"Read timeout while waiting for {endpoint} event {event_id}; retrying. elapsed={elapsed}s",
                flush=True,
            )
        except requests.RequestException as exc:
            elapsed = int(time.monotonic() - started_at)
            print(
                f"Transient error while waiting for {endpoint} event {event_id}: {exc}. elapsed={elapsed}s",
                flush=True,
            )
            time.sleep(5)

    if last_data is None and raw_lines:
        joined = "\n".join(raw_lines)
        try:
            last_data = json.loads(joined)
        except json.JSONDecodeError:
            pass

    if last_data is None:
        try:
            fallback_response = requests.get(
                f"{base_url}/gradio_api/call/{endpoint}/{event_id}",
                timeout=120,
            )
            fallback_response.raise_for_status()
            fallback_text = fallback_response.text.strip()
            if fallback_text:
                raw_lines.append(fallback_text)
                try:
                    last_data = fallback_response.json()
                except json.JSONDecodeError:
                    try:
                        last_data = json.loads(fallback_text)
                    except json.JSONDecodeError:
                        last_data = fallback_text
        except requests.RequestException:
            pass

    if last_data is None:
        preview = _preview("\n".join(raw_lines) if raw_lines else "")
        raise ValueError(f"No result returned for endpoint {endpoint}. Stream preview: {preview}")
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


def _artifact_candidates(reference: Any) -> list[str]:
    candidates: list[str] = []

    def visit(value: Any) -> None:
        if value is None:
            return
        if isinstance(value, str):
            stripped = value.strip()
            if stripped:
                candidates.append(stripped)
            return
        if isinstance(value, dict):
            preferred_keys = (
                "url",
                "path",
                "name",
                "image",
                "video",
                "file",
                "original",
                "preview",
            )
            for key in preferred_keys:
                if key in value:
                    visit(value[key])
            for nested_value in value.values():
                visit(nested_value)
            return
        if isinstance(value, list):
            for item in value:
                visit(item)

    visit(reference)

    deduped: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        deduped.append(candidate)
    return deduped


def _save_artifact(base_url: str, reference: Any, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    source = _artifact_url(base_url, reference)
    if not source:
        for candidate in _artifact_candidates(reference):
            source = _artifact_url(base_url, candidate)
            if source:
                break
    if not source:
        raise ValueError(
            "Could not resolve artifact location from API response. "
            f"Response preview: {_preview(reference)}"
        )

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
    print(f"Image API result preview: {_preview(gallery)}")
    return _save_artifact(base_url, gallery, output_path)


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
    height: int = 768,
    width: int = 512,
    inference_steps: int = 1,
    negative_prompt: str = "",
    guidance_scale_high: float = 0.0,
    guidance_scale_low: float = 0.0,
    video_quality: int = 1,
    scheduler: str = "FlowMatchEulerDiscrete",
    flow_shift: float = 0.5,
    fps: str = "16",
    display_result: bool = True,
) -> Path:
    event_id = _post_event(
        base_url,
        "generate_video",
        [
            {"path": str(image_path), "meta": {"_type": "gradio.FileData"}},
            {"path": str(image_path), "meta": {"_type": "gradio.FileData"}},
            prompt,
            inference_steps,
            negative_prompt,
            duration_seconds,
            guidance_scale_high,
            guidance_scale_low,
            seed,
            randomize_seed,
            video_quality,
            scheduler,
            flow_shift,
            fps,
            display_result,
        ],
    )
    result = _wait_for_event(base_url, "generate_video", event_id, timeout=1800)
    if not isinstance(result, list) or not result:
        raise ValueError("Video generation returned an unexpected payload")
    video_ref = result[0] if len(result) > 0 else None
    print(f"Video API result preview: {_preview(video_ref)}")
    return _save_artifact(base_url, video_ref, output_path)
