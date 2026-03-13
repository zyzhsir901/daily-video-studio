from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def copy_tree(src: Path, dst: Path, force: bool) -> None:
    if src.is_dir():
        if dst.exists():
            if not force:
                raise FileExistsError(f"Target already exists: {dst}")
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        return

    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and not force:
        raise FileExistsError(f"Target already exists: {dst}")
    shutil.copy2(src, dst)


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaffold the daily building video project into a target repo.")
    parser.add_argument("--target", required=True, help="Target repository root")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    template_root = script_dir.parent / "assets" / "repo-template"
    if not template_root.exists():
        raise RuntimeError(f"Template root not found: {template_root}")

    target_root = Path(args.target).resolve()
    target_root.mkdir(parents=True, exist_ok=True)

    copy_tree(
        template_root / "daily-building-video-agent",
        target_root / "daily-building-video-agent",
        force=args.force,
    )
    copy_tree(
        template_root / ".github" / "workflows" / "daily_building_video.yml",
        target_root / ".github" / "workflows" / "daily_building_video.yml",
        force=args.force,
    )

    print(f"Scaffolded building video project into {target_root}")


if __name__ == "__main__":
    main()
