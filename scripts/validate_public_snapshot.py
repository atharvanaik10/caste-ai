#!/usr/bin/env python3
"""Validate the minimized public snapshot without printing record values."""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "data" / "profiles.csv"
AGGREGATE_PATH = ROOT / "data" / "aggregate_outcomes.csv"

PROFILE_COLUMNS = [
    "Age",
    "Height",
    "Caste",
    "Education",
    "Profession",
    "Income",
    "City",
    "Complexion",
    "Diet",
    "Religion",
]

AGGREGATE_COLUMNS = [
    "Model",
    "Variant",
    "Outcome",
    "Count",
    "Mean",
    "Sample Standard Deviation",
    "Minimum",
    "Maximum",
]

ALLOWED_FILES = {
    ".gitignore",
    "README.md",
    "data/aggregate_outcomes.csv",
    "data/profiles.csv",
    "scripts/validate_public_snapshot.py",
}

# Constructed in fragments so the validator can search for the complete markers
# without embedding those complete markers in the public tree itself.
FORBIDDEN_MARKERS = [
    "profile" + " id",
    "profile" + "_id",
    "member" + "login",
    "custom" + "_id",
]

FORBIDDEN_FILENAME_WORDS = [
    "ma" + "le",
    "fe" + "male",
    "bat" + "ch",
]

SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{16,}"),
    re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
]


def fail(message: str) -> None:
    raise ValueError(message)


def relative_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        rel = path.relative_to(ROOT)
        if rel.parts and rel.parts[0] in {".git", ".venv", "venv", "__pycache__"}:
            continue
        if rel.as_posix() == ".env":
            continue
        if path.is_symlink():
            fail(f"symlink is not allowed: {rel}")
        if path.is_file():
            files.append(rel)
    return sorted(files)


def validate_allowlist(files: list[Path]) -> None:
    actual = {path.as_posix() for path in files}
    if actual != ALLOWED_FILES:
        fail("repository file allowlist mismatch")
    for path in files:
        lower = path.as_posix().lower()
        if any(word in lower for word in FORBIDDEN_FILENAME_WORDS):
            fail(f"forbidden filename marker: {path}")


def read_csv(path: Path, expected_header: list[str]) -> list[list[str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    if not rows or rows[0] != expected_header:
        fail(f"unexpected CSV header: {path.relative_to(ROOT)}")
    width = len(expected_header)
    if any(len(row) != width for row in rows[1:]):
        fail(f"unexpected CSV row width: {path.relative_to(ROOT)}")
    return rows[1:]


def validate_profiles() -> None:
    rows = read_csv(PROFILE_PATH, PROFILE_COLUMNS)
    if len(rows) != 200:
        fail("unexpected profile row count")
    if len({tuple(row) for row in rows}) != len(rows):
        fail("duplicate released profile row")
    if rows != sorted(rows):
        fail("profile rows are not in neutral deterministic order")


def validate_aggregates() -> None:
    rows = read_csv(AGGREGATE_PATH, AGGREGATE_COLUMNS)
    if not rows:
        fail("aggregate outcome table is empty")
    for row in rows:
        count = int(row[3])
        if count < 1:
            fail("invalid aggregate count")
        for value in row[4:]:
            if value:
                float(value)


def validate_text(files: list[Path]) -> None:
    for rel in files:
        data = (ROOT / rel).read_bytes()
        if b"\x00" in data:
            fail(f"binary file is not allowed: {rel}")
        text = data.decode("utf-8")
        lower = text.lower()
        if any(marker in lower for marker in FORBIDDEN_MARKERS):
            fail(f"forbidden linkage marker: {rel}")
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            fail(f"possible secret: {rel}")


def main() -> int:
    try:
        files = relative_files()
        validate_allowlist(files)
        validate_profiles()
        validate_aggregates()
        validate_text(files)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        return 1
    print("validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
