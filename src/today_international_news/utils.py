from __future__ import annotations

import json
import re
from pathlib import Path


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def slugify(value: str) -> str:
    lowered = value.lower()
    cleaned = re.sub(r"[^a-z0-9]+", "-", lowered)
    return cleaned.strip("-") or "item"


def extract_json_object(text: str) -> dict:
    decoder = json.JSONDecoder()
    stripped = text.strip()

    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)

    for index, char in enumerate(stripped):
        if char != "{":
            continue
        try:
            payload, _ = decoder.raw_decode(stripped[index:])
            if isinstance(payload, dict):
                return payload
        except json.JSONDecodeError:
            continue

    raise ValueError("Could not extract a JSON object from model output")

