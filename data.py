from __future__ import annotations

import csv
import pickle
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

from compilation import C

if TYPE_CHECKING:
    from compilation import Assembly

csv.field_size_limit(sys.maxsize)


class Label(Enum):
    NO_ERROR = 0
    RUNTIME_ERROR = 1


class DataPoint:
    def __init__(self, label: Label, c_code: C) -> None:
        self.label: Label = label
        self.c_code: C = c_code
        self.asm: list[Assembly] = []

    def as_dict(self) -> dict[str, str]:
        col_to_row: dict[str, str] = {"c_code": self.c_code}
        for asm in self.asm:
            compiler_version: str = asm.compiler.get_version()
            optimization_lvel: int = asm.optimization_level
            key: str = f"{asm.compiler.__class__.__name__}_{compiler_version}_O{optimization_lvel}"
            col_to_row[key] = asm

        return col_to_row


def clean_code(csv_line: str) -> str:
    c_code = csv_line.replace('""', '"')
    if c_code.startswith('"') and c_code.endswith('"'):
        c_code = c_code[1:-1]
    return subprocess.run(
        [
            "gcc",
            "-fpreprocessed",
            "-dD",
            "-E",
            "-P",
            "-",
        ],
        input=c_code.encode("utf-8"),
        check=True,
        capture_output=True,
    ).stdout.decode("utf-8")


def process_row(row: list[str]) -> DataPoint:
    code, label = row
    try:
        return DataPoint(Label(int(label)), C(clean_code(code)))
    except subprocess.CalledProcessError:
        return None


def read_data_csv(input_file: str) -> list[DataPoint]:
    with Path.open(input_file, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # skip column titles

        with ThreadPoolExecutor() as executor:
            results = list(executor.map(process_row, reader))

    return [dp for dp in results if dp is not None]


def to_pickle(input_file: str, datapoints: list[DataPoint]) -> None:
    with Path.open(input_file, "wb") as file:
        pickle.dump(datapoints, file)


def from_pickle(input_file: str) -> list[DataPoint]:
    with Path.open(input_file, "rb") as file:
        return pickle.load(file)
