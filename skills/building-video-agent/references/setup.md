# Setup Checklist

Use this reference after scaffolding the project.

## Required Secrets

- `GEMINI_API_KEY`

## Optional Secrets

- `GEMINI_MODEL`
- `BUILDING_SEGMENT_COUNT`
- `IMAGE_API_BASE_URL`
- `IMAGE_API_KEY`
- `IMAGE_RATIO`
- `VIDEO_API_BASE_URL`
- `VIDEO_API_KEY`
- `VIDEO_DURATION_SECONDS`

## Important Paths

- Project root: `daily-building-video-agent/`
- Workflow: `.github/workflows/daily_building_video.yml`
- Main pipeline: `daily-building-video-agent/src/daily_building_video/pipeline.py`
- Media API placeholders: `daily-building-video-agent/src/daily_building_video/media_clients.py`

## Expected Behavior

1. Before each run, old generated assets under `building-video-runs/` are deleted.
2. The daily workflow runs on schedule and on manual dispatch.
3. After generation, the workflow commits the fresh outputs back to the repository.
