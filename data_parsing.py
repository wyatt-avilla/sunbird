from __future__ import annotations

import csv
import sys
from enum import Enum
from pathlib import Path

from assembly import Assembly

csv.field_size_limit(sys.maxsize)


class Label(Enum):
    NO_ERROR = 0
    RUNTIME_ERROR = 1


class DataPoint:
    def __init__(self, label: Label, c_code: str) -> None:
        self.label: Label = label
        self.c_code: str = c_code
        self.asm: list[Assembly] = []


def clean_code(code: str) -> str:
    code = code.replace('""', '"')

    if code.startswith('"') and code.endswith('"'):
        code = code[1:-1]
    return code


def read_data_csv(input_file: str) -> list[DataPoint]:
    with Path.open(input_file, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # skip column titles

        return [
            DataPoint(Label(int(label)), clean_code(code)) for code, label in reader
        ]
