import csv, json
from pathlib import Path
from typing import Sequence
from pydantic import TypeAdapter
from .models import Paper
from .constants import FIELDS

def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

def save_json(path: Path, papers: Sequence[Paper]) -> None:
    ensure_parent(path); ta = TypeAdapter(list[Paper])
    path.write_text(ta.dump_json(list(papers), indent=2).decode(), encoding="utf-8")

def save_jsonl(path: Path, papers: Sequence[Paper]) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8") as f:
        for p in papers:
            f.write(json.dumps(p.model_dump(mode="json"), ensure_ascii=False)); f.write("\n")

def save_csv(path: Path, papers: Sequence[Paper]) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader()
        for p in papers: w.writerow(p.model_dump(mode="json"))

def save_by_suffix(path: Path, papers: Sequence[Paper]) -> None:
    suf = path.suffix.lower()
    if suf == ".jsonl": save_jsonl(path, papers)
    elif suf == ".csv": save_csv(path, papers)
    else: save_json(path, papers)
