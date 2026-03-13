from __future__ import annotations

import json
import os

from .gemini_client import GeminiClient
from .utils import extract_json_object


class DailyBuildingVideoCrew:
    """Sequential planner that mirrors the prior CrewAI-style workflow with Gemini."""

    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is required")
        model_name = os.getenv("GEMINI_MODEL") or "gemini-3.1-flash-lite-preview"
        self.client = GeminiClient(api_key=api_key, model_name=model_name)

    def _define_build_concept(
        self,
        report_date: str,
        seed: int,
        building_type: str,
        location_style: str,
        visual_style: str,
        tone: str,
        stage_sequence: list[str],
        segment_count: int,
        target_duration_seconds: float,
    ) -> dict:
        prompt = f"""
You are a construction concept planner.
Today is {report_date}. Seed is {seed}.

You are creating a short vertical AI video about one building being constructed from start to finish.

Input concept:
- Building type: {building_type}
- Location style: {location_style}
- Visual style: {visual_style}
- Tone: {tone}
- Stage sequence: {json.dumps(stage_sequence, ensure_ascii=False)}
- Segment count: {segment_count}
- Target total duration: {target_duration_seconds} seconds

Requirements:
- Keep the concept coherent as one single project, not multiple buildings.
- The final output should feel similar to an AI-generated building progress montage.
- Emphasize continuity across segments.
- Return JSON only.

Output schema:
{{
  "creative_summary": "string",
  "continuity_rules": ["string"],
  "audience_hook_angle": "string"
}}
""".strip()
        response = self.client.generate_text(prompt)
        return extract_json_object(response)

    def _create_storyboard_package(
        self,
        concept_payload: dict,
        building_type: str,
        location_style: str,
        visual_style: str,
        tone: str,
        stage_sequence: list[str],
        segment_count: int,
        target_duration_seconds: float,
    ) -> dict:
        prompt = f"""
You are a building process storyboard designer for a Chinese-speaking audience.

Using the concept below, build a production-ready short-video package.

Concept JSON:
{json.dumps(concept_payload, ensure_ascii=False, indent=2)}

Input brief:
- Building type: {building_type}
- Location style: {location_style}
- Visual style: {visual_style}
- Tone: {tone}
- Stage sequence: {json.dumps(stage_sequence, ensure_ascii=False)}
- Segment count: {segment_count}
- Target total duration: {target_duration_seconds} seconds

Hard requirements:
- Output must target a Chinese-speaking audience.
- Output valid JSON only.
- Build exactly {segment_count} segments.
- Each segment must map to one construction stage from the stage sequence.
- Maintain the same building identity across all shots.
- Keep narration concise and natural for short-video voiceover.
- Image prompts and video prompts must be in English.
- The result must be suitable for image generation followed by image-to-video generation.

Output schema:
{{
  "video_title": "string",
  "video_hook": "string",
  "creative_direction": "string",
  "music_direction": "string",
  "segments": [
    {{
      "rank": 1,
      "stage_name": "string",
      "shot_goal": "string",
      "narration": "string",
      "on_screen_text": "string",
      "image_prompt": "string in English",
      "video_prompt": "string in English",
      "duration_seconds": 3.2
    }}
  ]
}}
""".strip()
        response = self.client.generate_text(prompt)
        return extract_json_object(response)

    def _polish_visual_prompts(self, package_payload: dict) -> dict:
        prompt = f"""
You are an architectural visual director.

Review the current package below and improve only the visual production quality.

Package JSON:
{json.dumps(package_payload, ensure_ascii=False, indent=2)}

Requirements:
- Keep valid JSON only.
- Keep the same schema.
- Do not change the overall building concept.
- Improve continuity cues between segments.
- Make each shot visually distinct but clearly part of one construction timeline.
- Keep prompts realistic and appropriate for AI image and video generation.
""".strip()
        response = self.client.generate_text(prompt)
        return extract_json_object(response)

    def _review_package(self, package_payload: dict, segment_count: int) -> dict:
        prompt = f"""
You are a short video executive producer reviewing a building process package.

Review the generated JSON package below.

Package JSON:
{json.dumps(package_payload, ensure_ascii=False, indent=2)}

Requirements:
- Keep valid JSON only.
- Keep the same schema.
- Ensure there are exactly {segment_count} segments.
- Ensure the pacing feels like a roughly 19-second vertical short video.
- Ensure the Chinese narration is concise.
- Ensure the visuals describe plausible construction progress.
- Remove repetition and weak shots.
""".strip()
        response = self.client.generate_text(prompt)
        return extract_json_object(response)

    def run(
        self,
        report_date: str,
        seed: int,
        building_type: str,
        location_style: str,
        visual_style: str,
        tone: str,
        stage_sequence: list[str],
        segment_count: int,
        target_duration_seconds: float,
    ) -> dict:
        concept = self._define_build_concept(
            report_date=report_date,
            seed=seed,
            building_type=building_type,
            location_style=location_style,
            visual_style=visual_style,
            tone=tone,
            stage_sequence=stage_sequence,
            segment_count=segment_count,
            target_duration_seconds=target_duration_seconds,
        )
        draft = self._create_storyboard_package(
            concept_payload=concept,
            building_type=building_type,
            location_style=location_style,
            visual_style=visual_style,
            tone=tone,
            stage_sequence=stage_sequence,
            segment_count=segment_count,
            target_duration_seconds=target_duration_seconds,
        )
        polished = self._polish_visual_prompts(package_payload=draft)
        return self._review_package(package_payload=polished, segment_count=segment_count)
