from __future__ import annotations

import json
import os

from .gemini_client import GeminiClient
from .utils import extract_json_object


class TodayInternationalNewsCrew:
    """Sequential planner that mirrors the multi-agent workflow with Gemini."""

    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is required")
        model_name = os.getenv("GEMINI_MODEL") or "gemini-3.1-flash-lite-preview"
        self.client = GeminiClient(api_key=api_key, model_name=model_name)

    def _select_news(self, report_date: str, news_digest: str, max_news: int) -> dict:
        prompt = f"""
You are a global news editor.
Today is {report_date}.

Review the candidate world news feed below and select the highest-signal stories.

Candidate stories:
{news_digest}

Requirements:
- Select exactly {max_news} stories unless the feed clearly has fewer meaningful items.
- Prioritize geopolitical, military, diplomatic, macroeconomic, energy, and humanitarian impact.
- Avoid duplicate angles about the same event unless they are meaningfully different.
- Return JSON only.

Output schema:
{{
  "selection_rationale": "string",
  "selected_stories": [
    {{
      "rank": 1,
      "headline": "string",
      "source": "string",
      "source_link": "string",
      "why_selected": "string"
    }}
  ]
}}
""".strip()
        response = self.client.generate_text(prompt)
        return extract_json_object(response)

    def _create_video_package(self, selected_payload: dict, max_news: int) -> dict:
        prompt = f"""
You are a short video script producer for a Chinese-speaking audience.

Build a structured short-video package from the selected stories below.

Selected stories JSON:
{json.dumps(selected_payload, ensure_ascii=False, indent=2)}

Requirements:
- Output must target a Chinese-speaking audience.
- The whole package should feel like one coherent "global big events" video.
- Do not invent facts beyond the selected story context.
- Keep it concise and suitable for a short video.
- Return JSON only.

Output schema:
{{
  "video_title": "string",
  "video_hook": "string",
  "global_outlook": "string",
  "segments": [
    {{
      "rank": 1,
      "headline": "string",
      "source": "string",
      "source_link": "string",
      "why_it_matters": "string",
      "narration": "string",
      "on_screen_text": "string",
      "image_prompt": "string in English",
      "video_prompt": "string in English",
      "duration_seconds": 3.0
    }}
  ]
}}

Use no more than {max_news} segments.
""".strip()
        response = self.client.generate_text(prompt)
        return extract_json_object(response)

    def _visual_polish_package(self, package_payload: dict) -> dict:
        prompt = f"""
You are a visual director for current-affairs short videos.

Review the structured short-video package below and improve only the visual production fields.

Package JSON:
{json.dumps(package_payload, ensure_ascii=False, indent=2)}

Requirements:
- Keep valid JSON only.
- Keep the same schema.
- Keep all factual fields aligned with the existing package.
- Improve visual distinctiveness across segments.
- Ensure image prompts and video prompts are realistic, cinematic, and safe for news production.
- Do not add unsupported factual claims.
""".strip()
        response = self.client.generate_text(prompt)
        return extract_json_object(response)

    def _review_video_package(self, package_payload: dict, max_news: int) -> dict:
        prompt = f"""
You are an executive producer reviewing a global news short-video package.

Review the generated JSON package below.

Package JSON:
{json.dumps(package_payload, ensure_ascii=False, indent=2)}

Requirements:
- Keep valid JSON only.
- Keep the same schema.
- Ensure there are no more than {max_news} segments.
- Ensure each segment is visually distinct.
- Ensure the Chinese narration is concise and natural.
- Ensure the package reads like a standard production handoff for image and video generation.
""".strip()
        response = self.client.generate_text(prompt)
        return extract_json_object(response)

    def run(self, report_date: str, news_digest: str, max_news: int) -> dict:
        selected = self._select_news(report_date=report_date, news_digest=news_digest, max_news=max_news)
        draft = self._create_video_package(selected_payload=selected, max_news=max_news)
        polished = self._visual_polish_package(package_payload=draft)
        return self._review_video_package(package_payload=polished, max_news=max_news)
