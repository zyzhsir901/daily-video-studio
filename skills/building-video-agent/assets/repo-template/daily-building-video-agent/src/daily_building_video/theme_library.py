from __future__ import annotations

import random
from datetime import datetime

from .models import BuildConcept


BUILDING_TYPES = [
    "glass office tower",
    "modern museum",
    "luxury riverside apartment",
    "urban library",
    "boutique hotel",
    "airport terminal",
    "stadium complex",
    "high-speed rail station",
]

LOCATION_STYLES = [
    "dense Asian city block",
    "European waterfront district",
    "desert-edge new town",
    "coastal financial center",
    "mountain valley township",
    "industrial redevelopment zone",
]

VISUAL_STYLES = [
    "cinematic realism",
    "architectural visualization realism",
    "drone-style construction documentary",
    "time-lapse inspired photorealism",
]

TONES = [
    "efficient and modern",
    "ambitious and premium",
    "clean and futuristic",
    "precise and engineering-focused",
]

STAGE_SETS = [
    ["site clearing", "foundation work", "steel structure rising", "facade installation", "interior finishing", "completed reveal"],
    ["ground excavation", "core structure", "floor-by-floor expansion", "glass curtain wall", "landscape finishing", "opening-day reveal"],
    ["empty lot setup", "crane-led assembly", "main shell completion", "detail finishing", "lighting and surroundings", "final hero shot"],
]


def build_daily_concept(segment_count: int, now: datetime | None = None) -> BuildConcept:
    current = now or datetime.now()
    date_key = current.strftime("%Y-%m-%d")
    seed = int(current.strftime("%Y%m%d"))
    rng = random.Random(seed)

    stage_sequence = list(rng.choice(STAGE_SETS))[:segment_count]
    while len(stage_sequence) < segment_count:
        stage_sequence.append(stage_sequence[-1])

    return BuildConcept(
        date_key=date_key,
        seed=seed,
        building_type=rng.choice(BUILDING_TYPES),
        location_style=rng.choice(LOCATION_STYLES),
        visual_style=rng.choice(VISUAL_STYLES),
        tone=rng.choice(TONES),
        stage_sequence=stage_sequence,
        total_duration_seconds=round(segment_count * 3.2, 1),
    )
