from __future__ import annotations

from pathlib import Path
import re

from blog_utils import format_date, parse_metadata

ROOT = Path(__file__).resolve().parents[1]
BLOG_DIR = ROOT / "blog" / "posts"
HOME_FILE = ROOT / "index.html"
BLOG_INDEX_FILE = ROOT / "blog" / "index.html"

HOME_START = "<!-- HOMEPOSTS:START -->"
HOME_END = "<!-- HOMEPOSTS:END -->"
BLOG_START = "<!-- POSTS:START -->"
BLOG_END = "<!-- POSTS:END -->"

HOME_LIMIT = 2


def build_card(meta, href_prefix: str) -> str:
    date_display = format_date(meta.date)
    return (
        "<article class=\"post-card\">\n"
        "  <div class=\"post-meta\">\n"
        f"    <span>{date_display}</span>\n"
        f"    <span class=\"pill\">{meta.label}</span>\n"
        "  </div>\n"
        f"  <h3>{meta.title}</h3>\n"
        f"  <p>\n    {meta.summary}\n  </p>\n"
        f"  <a class=\"text-link\" href=\"{href_prefix}{meta.filename}\">\n"
        "    Read the post\n"
        "  </a>\n"
        "</article>"
    )


def replace_block(text: str, start: str, end: str, block: str) -> str:
    pattern = re.compile(
        rf"(^[ \t]*){re.escape(start)}\s*$(.*?)^[ \t]*{re.escape(end)}\s*$",
        re.M | re.S,
    )
    match = pattern.search(text)
    if not match:
        raise ValueError(f"Missing block markers for {start}")

    indent = match.group(1)
    indented_block = "\n".join(f"{indent}{line}" if line else "" for line in block.splitlines())
    replacement = f"{indent}{start}\n{indented_block}\n{indent}{end}"
    return text[: match.start()] + replacement + text[match.end() :]


def main() -> None:
    posts = []
    for path in sorted(BLOG_DIR.glob("*.html")):
        meta = parse_metadata(path)
        posts.append(meta)

    posts.sort(key=lambda p: p.date, reverse=True)

    blog_cards = "\n\n".join(build_card(meta, "posts/") for meta in posts)
    home_cards = "\n\n".join(build_card(meta, "blog/posts/") for meta in posts[:HOME_LIMIT])

    home_text = HOME_FILE.read_text(encoding="utf-8")
    home_text = replace_block(home_text, HOME_START, HOME_END, home_cards)
    HOME_FILE.write_text(home_text, encoding="utf-8")

    blog_index_text = BLOG_INDEX_FILE.read_text(encoding="utf-8")
    blog_index_text = replace_block(blog_index_text, BLOG_START, BLOG_END, blog_cards)
    BLOG_INDEX_FILE.write_text(blog_index_text, encoding="utf-8")


if __name__ == "__main__":
    main()
