from __future__ import annotations

import json
import subprocess


class GeminiClient:
    def __init__(self, api_key: str, model_name: str) -> None:
        self.api_key = api_key
        self.model_name = model_name

    def generate_text(self, prompt: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent"
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt,
                        }
                    ]
                }
            ]
        }
        command = [
            "curl",
            url,
            "-H",
            f"x-goog-api-key: {self.api_key}",
            "-H",
            "Content-Type: application/json",
            "-X",
            "POST",
            "-d",
            json.dumps(payload, ensure_ascii=False),
        ]
        response = subprocess.run(command, capture_output=True, text=True, check=True)
        data = json.loads(response.stdout)
        candidates = data.get("candidates") or []
        if not candidates:
            raise ValueError(f"Gemini returned no candidates: {response.stdout}")
        content = candidates[0].get("content") or {}
        parts = content.get("parts") or []
        texts = [part.get("text", "") for part in parts if isinstance(part, dict)]
        result = "\n".join(text for text in texts if text).strip()
        if not result:
            raise ValueError(f"Gemini returned no text parts: {response.stdout}")
        return result
