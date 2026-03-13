from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import html
import re
from typing import Iterable
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


RSS_SOURCES = [
    ("Reuters World", "https://feeds.reuters.com/Reuters/worldNews"),
    ("Associated Press World", "https://feeds.apnews.com/rss/apf-intlnews"),
    ("BBC World", "http://feeds.bbci.co.uk/news/world/rss.xml"),
]


@dataclass
class NewsItem:
    source: str
    title: str
    link: str
    published_at: str
    summary: str


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


def fetch_rss_items(limit_per_source: int = 8) -> list[NewsItem]:
    items: list[NewsItem] = []
    headers = {"User-Agent": "daily-video-studio/1.0"}

    for source_name, url in RSS_SOURCES:
        request = Request(url, headers=headers)
        with urlopen(request, timeout=20) as response:
            payload = response.read()

        root = ET.fromstring(payload)
        entries = root.findall(".//item")
        for entry in entries[:limit_per_source]:
            title = _clean_text(_child_text(entry, ["title"]))
            link = _clean_text(_child_text(entry, ["link"]))
            published = _clean_text(_child_text(entry, ["pubDate", "published"]))
            summary = _clean_text(_child_text(entry, ["description", "summary"]))
            if not title or not link:
                continue
            items.append(
                NewsItem(
                    source=source_name,
                    title=title,
                    link=link,
                    published_at=published,
                    summary=summary[:500],
                )
            )

    return dedupe_items(items)


def dedupe_items(items: list[NewsItem]) -> list[NewsItem]:
    seen_titles: set[str] = set()
    unique_items: list[NewsItem] = []
    for item in items:
        normalized = re.sub(r"[^a-z0-9]+", "", item.title.lower())
        if normalized in seen_titles:
            continue
        seen_titles.add(normalized)
        unique_items.append(item)
    return unique_items


def build_digest(items: list[NewsItem], max_items: int = 18) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    selected = items[:max_items]
    lines = [f"新闻抓取时间：{now}", ""]
    for index, item in enumerate(selected, start=1):
        lines.append(f"{index}. 来源：{item.source}")
        lines.append(f"   标题：{item.title}")
        if item.published_at:
            lines.append(f"   发布时间：{item.published_at}")
        if item.summary:
            lines.append(f"   导语：{item.summary}")
        lines.append(f"   链接：{item.link}")
        lines.append("")
    return "\n".join(lines).strip()

