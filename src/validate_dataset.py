#!/usr/bin/env python3
"""Validate the structure and labels in a FEVER JSONL file."""

import argparse
import json
from collections import Counter
from pathlib import Path

LABELS = {"SUPPORTS", "REFUTES", "NOT ENOUGH INFO"}


def validate(path: Path) -> tuple[int, Counter[str]]:
    counts: Counter[str] = Counter()
    total = 0
    with path.open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"line {line_number}: invalid JSON: {error.msg}") from error
            for field in ("id", "claim", "label"):
                if field not in record:
                    raise ValueError(f"line {line_number}: missing required field '{field}'")
            if not isinstance(record["claim"], str) or not record["claim"].strip():
                raise ValueError(f"line {line_number}: claim must be a non-empty string")
            label = record["label"]
            if label not in LABELS:
                raise ValueError(f"line {line_number}: unknown label {label!r}")
            if "evidence" in record and not isinstance(record["evidence"], list):
                raise ValueError(f"line {line_number}: evidence must be a list")
            counts[label] += 1
            total += 1
    return total, counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jsonl", type=Path, help="FEVER JSONL dataset to validate")
    args = parser.parse_args()
    if not args.jsonl.is_file():
        parser.error(f"file not found: {args.jsonl}")
    try:
        total, counts = validate(args.jsonl)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Validation failed: {error}\n")
    print(f"Validation passed: {args.jsonl}")
    print(f"Records: {total:,}")
    for label in sorted(LABELS):
        print(f"  {label}: {counts[label]:,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
