from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re


@dataclass(frozen=True)
class PostMeta:
    title: str
    date: str
    label: str
    summary: str
    filename: str


def parse_metadata(path: Path) -> PostMeta:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"<!--\s*(.*?)\s*-->", text, re.S)
    if not match:
        raise ValueError(f"Missing metadata comment in {path}")

    raw = match.group(1)
    data: dict[str, str] = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()

    missing = [k for k in ("title", "date", "label", "summary") if k not in data]
    if missing:
        raise ValueError(f"Missing fields {missing} in {path}")

    return PostMeta(
        title=data["title"],
        date=data["date"],
        label=data["label"],
        summary=data["summary"],
        filename=path.name,
    )


def format_date(date_str: str) -> str:
    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%b %-d, %Y")
