from __future__ import annotations

from pathlib import Path
import os
import shutil

from blog_utils import parse_metadata
import build_blog_index

ROOT = Path(__file__).resolve().parents[1]
SCHEDULED_DIR = ROOT / "scheduled_posts"
BLOG_DIR = ROOT / "blog" / "posts"


def main() -> None:
    if not SCHEDULED_DIR.exists():
        print("No scheduled_posts directory found. Nothing to publish.")
        return

    scheduled_files = sorted(SCHEDULED_DIR.glob("*.html"))
    if not scheduled_files:
        print("No scheduled posts found.")
        return

    existing = {path.name for path in BLOG_DIR.glob("*.html")}
    next_post = None
    for path in scheduled_files:
        if path.name not in existing:
            next_post = path
            break

    if next_post is None:
        print("No unpublished scheduled posts.")
        return

    BLOG_DIR.mkdir(parents=True, exist_ok=True)
    destination = BLOG_DIR / next_post.name
    shutil.copy2(next_post, destination)

    meta = parse_metadata(destination)
    build_blog_index.main()

    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as handle:
            handle.write("published=true\n")
            handle.write(f"title={meta.title}\n")
            handle.write(f"filename={meta.filename}\n")
    else:
        print(f"Published: {meta.title}")


if __name__ == "__main__":
    main()
