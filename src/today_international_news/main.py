from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path

from dotenv import load_dotenv

from .crew import TodayInternationalNewsCrew
from .news_sources import build_digest, fetch_rss_items


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _reports_dir() -> Path:
    return _project_root() / "today-international-news" / "reports"


def _render_final_report(report_date: str, content: str) -> str:
    if content.lstrip().startswith("# "):
        return content
    return f"# Daily International News {report_date}\n\n{content.strip()}\n"


def run() -> Path:
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is required")

    report_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    items = fetch_rss_items()
    digest = build_digest(items)

    result = TodayInternationalNewsCrew().crew().kickoff(
        inputs={
            "report_date": report_date,
            "news_digest": digest,
        }
    )

    report_content = _render_final_report(report_date, str(result))
    reports_dir = _reports_dir()
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / f"{report_date}.md"
    report_path.write_text(report_content, encoding="utf-8")
    return report_path


if __name__ == "__main__":
    path = run()
    print(f"Report saved to {path}")
