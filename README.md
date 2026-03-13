# Daily Video Studio

This repository contains a CrewAI pipeline for producing one short-form "global international news" video package per run.

## Pipeline

The pipeline follows a standard editorial workflow:

1. Fetch Google News world RSS headlines
2. Parse and deduplicate candidate stories
3. Use CrewAI to select the top 8 stories and build a structured video package
4. Generate one image per story
5. Generate one short motion clip per story
6. Burn subtitles onto each story clip
7. Add an intro title card and a follow-like-save outro card
8. Concatenate clips into a final video with FFmpeg
9. Save the run outputs into the repository

## News Inputs

- RSS feed:
  `https://news.google.com/rss/headlines/section/topic/WORLD?hl=en-US&gl=US&ceid=US:en`
- Topic page:
  `https://news.google.com/topics/CAAqKggKIiRDQkFTRlFvSUwyMHZNRGx1YlY4U0JXVnVMVWRDR2dKRFFTZ0FQAQ?hl=en-US&gl=US&ceid=US%3Aen`

## Outputs

Each run writes to:

- `today-international-news/runs/YYYY-MM-DD/inputs/`
- `today-international-news/runs/YYYY-MM-DD/planning/`
- `today-international-news/runs/YYYY-MM-DD/script/`
- `today-international-news/runs/YYYY-MM-DD/assets/images/`
- `today-international-news/runs/YYYY-MM-DD/assets/clips/`
- `today-international-news/runs/YYYY-MM-DD/outputs/`

Main artifacts:

- `video_package.json`
- `video_script.md`
- `manifest.json`
- `intro.mp4`
- `outro.mp4`
- `final_video.mp4` when clip generation succeeds

## Local Run

Use Python 3.10 or newer.

```bash
pip install -r requirements.txt
copy .env.example .env
set PYTHONPATH=today-international-news
python -m today_international_news.main
```

## Environment

Required:

- `GEMINI_API_KEY`

Optional:

- `GEMINI_MODEL=gemini-3.1-flash-lite-preview`
- `PIPELINE_MAX_NEWS=8`
- `IMAGE_API_BASE_URL=https://tongyi-mai-z-image-turbo.hf.space`
- `IMAGE_RATIO=768x1024 ( 3:4 )`
- `VIDEO_API_BASE_URL=https://alexnasa-ltx-2-turbo.hf.space`
- `VIDEO_HIGH_RES=false`
- `VIDEO_DURATION_SECONDS=3.0`
- `VIDEO_HEIGHT=768`
- `VIDEO_WIDTH=512`
- `VIDEO_INFERENCE_STEPS=1`
- `VIDEO_NEGATIVE_PROMPT=`
- `VIDEO_GENERATION_MODE=Image-to-Video`
- `VIDEO_CAMERA_LORA=No LoRA`
- `VIDEO_ENHANCE_PROMPT=true`
- `VIDEO_DISPLAY_RESULT=true`
- `VIDEO_EVENT_TIMEOUT_SECONDS=120`

## GitHub Actions

The workflow supports manual runs and a daily schedule.

Repository secrets to configure:

- `GEMINI_API_KEY`
- `GEMINI_MODEL` optional
- `IMAGE_API_BASE_URL` optional
- `IMAGE_RATIO` optional
- `VIDEO_API_BASE_URL` optional
- `VIDEO_HIGH_RES` optional
- `VIDEO_DURATION_SECONDS` optional
- `VIDEO_HEIGHT` optional
- `VIDEO_WIDTH` optional
- `VIDEO_INFERENCE_STEPS` optional
- `VIDEO_NEGATIVE_PROMPT` optional
- `VIDEO_GENERATION_MODE` optional
- `VIDEO_CAMERA_LORA` optional
- `VIDEO_ENHANCE_PROMPT` optional
- `VIDEO_DISPLAY_RESULT` optional
- `VIDEO_EVENT_TIMEOUT_SECONDS` optional

Important:

- The image API is public by default in this project.
- The default video API now points to the public `alexnasa-ltx-2-turbo` Hugging Face Space.
- Default image and video settings are portrait-oriented.
- Before each run, the pipeline clears the previous generated content under `today-international-news/runs/` and then commits the new images, clips, manifests, and final video back to GitHub.
- The workflow code now lives under `today-international-news/today_international_news/`.
