# Daily Building Video Agent

This project contains a Crew-style sequential pipeline for generating one short-form "building process" video package per run.

The pipeline is designed for AI-generated construction videos similar to the reference clip in the workspace:

- vertical short-video format
- about 19 seconds total duration
- several short construction-stage shots
- one coherent build narrative from start to finish

## What It Produces

Each run creates a dated output folder with:

- a random building concept
- a structured storyboard package
- Chinese narration and on-screen text
- English image prompts
- English image-to-video prompts
- an asset manifest
- a final video when image/video APIs and FFmpeg are available

Artifacts are written under `building-video-runs/YYYY-MM-DD/`.

## Pipeline

1. Pick a daily random construction concept from local building/stage/style pools
2. Use the Gemini-based multi-role planner to turn the concept into a vertical short-video package
3. Save planning and script artifacts
4. Optionally generate one image per segment
5. Optionally generate one short clip per segment
6. Optionally concatenate clips into the final video
7. Clear previous generated outputs before each new run
8. Commit the latest outputs back to GitHub when run by GitHub Actions

## Reference Video Analysis

The sample video in the sibling project appears to follow this production logic:

1. Decide one simple narrative arc:
   foundation -> structure -> facade -> completion
2. Break the arc into 5 to 6 short shots
3. Keep each shot around 3 to 4 seconds
4. Use one visual subject throughout so the audience reads it as one continuous build
5. Concatenate all shots into a single vertical short video

This agent uses the same idea, but swaps current news topics for construction concepts.

## Local Run

```bash
pip install -r requirements.txt
copy .env.example .env
python -m src.daily_building_video.main
```

## Environment

Required:

- `GEMINI_API_KEY`

Optional:

- `GEMINI_MODEL=gemini-3.1-flash-lite-preview`
- `BUILDING_SEGMENT_COUNT=6`
- `IMAGE_API_BASE_URL=`
- `IMAGE_API_KEY=`
- `IMAGE_RATIO=720x1280`
- `VIDEO_API_BASE_URL=`
- `VIDEO_API_KEY=`
- `VIDEO_DURATION_SECONDS=3.2`
- `OUTPUT_FPS=24`

When image/video APIs are empty, the pipeline still produces planning files and a manifest. Asset generation is skipped cleanly.

## GitHub Actions

The project includes a daily workflow at `.github/workflows/daily_building_video.yml`.

It does three important things:

1. runs on a daily schedule and also supports manual trigger
2. clears `building-video-runs/` before generation
3. commits the latest generated outputs back to the repository

Configure these repository secrets before enabling scheduled runs:

- `GEMINI_API_KEY`
- `GEMINI_MODEL` optional
- `BUILDING_SEGMENT_COUNT` optional
- `IMAGE_API_BASE_URL` optional
- `IMAGE_API_KEY` optional
- `IMAGE_RATIO` optional
- `VIDEO_API_BASE_URL` optional
- `VIDEO_API_KEY` optional
- `VIDEO_DURATION_SECONDS` optional
