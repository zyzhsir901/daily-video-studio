# Daily Video Studio

This repository includes a CrewAI-based agent that produces a daily Chinese briefing for major international news and stores the result in `today-international-news/reports/`.

## What It Does

- Pulls headlines from a small set of international RSS feeds
- Deduplicates and trims the input
- Uses CrewAI to select the most important items
- Writes a markdown report for the current day
- Can run locally or on GitHub Actions

## Project Layout

- `src/today_international_news/`: CrewAI app code
- `today-international-news/reports/`: generated daily reports
- `.github/workflows/daily_international_news.yml`: scheduled workflow

## Local Run

1. Install Python 3.10+.
2. Create a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set environment variables:

```bash
copy .env.example .env
```

5. Run:

```bash
python -m src.today_international_news.main
```

## GitHub Actions Setup

Add this repository secret:

- `OPENAI_API_KEY`: API key for the model used by CrewAI
- `OPENAI_MODEL_NAME`: optional model override, for example `gpt-4o-mini`

The workflow supports:

- manual runs from GitHub Actions
- a daily scheduled run at 08:00 UTC

## Notes

- CrewAI officially requires Python 3.10+.
- Generated reports are committed back to the repository by the workflow.
