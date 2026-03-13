from __future__ import annotations

from .pipeline import run_pipeline


if __name__ == "__main__":
    run_root = run_pipeline()
    print(f"Run saved to {run_root}")

