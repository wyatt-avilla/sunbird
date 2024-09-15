from __future__ import annotations

import csv
import sys
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from compilation import Assembly, C

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
        col_to_row: dict[str, str] = {"c_code": self.c_code.source}
        for asm in self.asm:
            compiler_version: str = asm.compiler.get_version()
            optimization_lvel: int = asm.optimization_level
            key: str = f"{asm.compiler.__class__.__name__}_{compiler_version}_O{optimization_lvel}"
            col_to_row[key] = asm.source

        return col_to_row
