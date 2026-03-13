---
name: building-video-agent
description: Use when the user wants to scaffold, update, or run a daily AI-generated building-process video project with Gemini planning, optional image/video APIs, FFmpeg assembly, and GitHub Actions auto-publishing. Trigger on requests like "build a building video agent", "create a daily construction video pipeline", "set up GitHub Actions for AI video generation", or "turn this building video project into a reusable Codex workflow/skill".
---

# Building Video Agent

## Overview

This skill installs or refreshes a ready-to-run building video project in the current workspace. It bundles a project template, a GitHub Actions workflow, and a scaffold script so Codex can create the same daily building-process video pipeline without rewriting the structure from scratch.

## When To Use

- The user wants a new AI building-process video generator project
- The user wants the existing building video pipeline copied into another repo
- The user wants a daily scheduled GitHub Actions workflow that commits generated assets back to GitHub
- The user wants this workflow converted into a reusable Codex-installable skill

## Workflow

1. Confirm whether the user wants a fresh scaffold or changes to an existing building-video project.
2. If scaffolding is needed, run `scripts/scaffold_project.py --target <workspace>`.
3. The script copies the bundled repo template:
   - `daily-building-video-agent/`
   - `.github/workflows/daily_building_video.yml`
4. After scaffolding, review `.env.example`, workflow secrets, and any API placeholders the user wants to wire up.
5. If the project already exists, modify files in place rather than re-copying the whole template.
6. Prefer keeping the generated project self-contained and repo-ready.

## Scaffold Command

Default usage:

```bash
python scripts/scaffold_project.py --target .
```

Useful flags:

- `--target <path>`: target repository root
- `--force`: overwrite existing target files

The scaffold script is deterministic. Use it instead of manually copying files whenever the user is creating the project from this skill.

## Bundled Template

The full starter project lives under `assets/repo-template/`.

Important contents:

- `assets/repo-template/daily-building-video-agent/`
- `assets/repo-template/.github/workflows/daily_building_video.yml`

Use the asset template as the source of truth for new scaffolds. If the skill is updated, refresh the asset template to match the latest working project.

## Post-Scaffold Checks

After copying the template:

1. Check `daily-building-video-agent/.env.example`
2. Confirm `GEMINI_API_KEY` and optional media API secrets
3. Confirm whether the user wants the workflow schedule changed
4. Verify the target repo wants generated assets committed back to GitHub
5. If the user requests API integration, edit `src/daily_building_video/media_clients.py`

## References

- Setup and secrets checklist: `references/setup.md`

## Rules

- Do not rebuild the project from scratch if the scaffold script can copy it safely.
- Do not invent image or video API payloads; leave placeholders when the user has not provided provider details.
- Keep the workflow in the target repo root `.github/workflows/`.
- Keep generated assets under `daily-building-video-agent/building-video-runs/`.
