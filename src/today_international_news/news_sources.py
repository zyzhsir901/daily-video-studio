from __future__ import annotations

from datetime import datetime, timezone
import html
import re
from typing import Iterable
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

from .models import NewsItem


RSS_URL = "https://news.google.com/rss/headlines/section/topic/WORLD?hl=en-US&gl=US&ceid=US:en"
NEWS_SOURCE_URL = (
    "https://news.google.com/topics/"
    "CAAqKggKIiRDQkFTRlFvSUwyMHZNRGx1YlY4U0JXVnVMVWRDR2dKRFFTZ0FQAQ"
    "?hl=en-US&gl=US&ceid=US%3Aen"
)


def _clean_text(value: str) -> str:
    text = html.unescape(value or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _child_text(element: ET.Element, names: Iterable[str]) -> str:
    for name in names:
        child = element.find(name)
        if child is not None and child.text:
            return child.text.strip()
    return ""


def _split_google_title(title: str) -> tuple[str, str]:
    if " - " not in title:
        return title, "Google News"
    headline, source = title.rsplit(" - ", 1)
    return headline.strip(), source.strip()


def fetch_google_news_items(limit: int = 30) -> list[NewsItem]:
    request = Request(RSS_URL, headers={"User-Agent": "daily-video-studio/1.0"})
    with urlopen(request, timeout=20) as response:
        payload = response.read()

    root = ET.fromstring(payload)
    items: list[NewsItem] = []
    for entry in root.findall(".//item")[:limit]:
        raw_title = _clean_text(_child_text(entry, ["title"]))
        headline, source = _split_google_title(raw_title)
        link = _clean_text(_child_text(entry, ["link"]))
        published = _clean_text(_child_text(entry, ["pubDate"]))
        summary = _clean_text(_child_text(entry, ["description"]))
        if not headline or not link:
            continue
        items.append(
            NewsItem(
                source=source,
                title=headline,
                link=link,
                published_at=published,
                summary=summary[:600],
            )
        )

    return dedupe_items(items)


def dedupe_items(items: list[NewsItem]) -> list[NewsItem]:
    seen: set[str] = set()
    unique: list[NewsItem] = []
    for item in items:
        key = re.sub(r"[^a-z0-9]+", "", item.title.lower())
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def build_digest(items: list[NewsItem], max_items: int = 24) -> str:
    captured_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"Captured at: {captured_at}",
        f"Topic page: {NEWS_SOURCE_URL}",
        "",
    ]
    for index, item in enumerate(items[:max_items], start=1):
        lines.append(f"{index}. Headline: {item.title}")
        lines.append(f"   Source: {item.source}")
        if item.published_at:
            lines.append(f"   Published: {item.published_at}")
        if item.summary:
            lines.append(f"   Summary: {item.summary}")
        lines.append(f"   Link: {item.link}")
        lines.append("")
    return "\n".join(lines).strip()

