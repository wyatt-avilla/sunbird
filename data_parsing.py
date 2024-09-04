from __future__ import annotations

import csv
import sys
from pathlib import Path

csv.field_size_limit(sys.maxsize)


def clean_code(code: str) -> str:
    code = code.replace('""', '"')

    if code.startswith('"') and code.endswith('"'):
        code = code[1:-1]
    return code


def read_data_csv(input_file: str) -> list[tuple[str, int]]:
    with Path.open(input_file, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # skip column titles

        return [(clean_code(code), int(label)) for code, label in reader]
