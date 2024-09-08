from __future__ import annotations

import csv
import sys
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from compilation import Assembly

csv.field_size_limit(sys.maxsize)


class Label(Enum):
    NO_ERROR = 0
    RUNTIME_ERROR = 1


class DataPoint:
    def __init__(self, label: Label, c_code: str) -> None:
        self.label: Label = label
        self.c_code: str = c_code
        self.asm: list[Assembly] = []

    def as_dict(self) -> dict[str, str]:
        col_to_row: dict[str, str] = {"c_code": self.c_code}
        for asm in self.asm:
            compiler_version: str = asm.compiler.get_version()
            optimization_lvel: int = asm.optimization_level
            key: str = f"{asm.compiler.__class__.__name__}_{compiler_version}_O{optimization_lvel}"
            col_to_row[key] = asm

        return col_to_row


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


def write_data_csv(input_file: str, rows: list[dict[str, str]]) -> None:
    with Path.open(input_file, mode="w", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=rows[0].keys(),
            quoting=csv.QUOTE_MINIMAL,
        )

        writer.writeheader()
        writer.writerows(rows)
