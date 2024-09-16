from __future__ import annotations

import csv
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from itertools import islice
from pathlib import Path
from typing import Generator

from compilation import GCC, C, Clang, CompilationError, Compiler
from datapoint import DataPoint, Label


class DatasetIterator:
    def __init__(self, csv_path: str, *, debug_logging: bool = False) -> None:
        csv.field_size_limit(sys.maxsize)
        if not csv_path.endswith(".csv"):
            invalid_extension_error = "expected a csv file"
            raise ValueError(invalid_extension_error)

        self.rows = self.__csv_row_iterator_from(csv_path)
        self.enable_logging = debug_logging

    def __csv_row_iterator_from(
        self,
        input_file: str,
    ) -> Generator[list[str], None, None]:
        with Path(input_file).open(mode="r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # skip column titles
            yield from reader

    def __clean_code(self, csv_line: str) -> str:
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

    def __datapoint_from_row(self, row: list[str]) -> DataPoint | None:
        code, label = row
        try:
            return DataPoint(Label(int(label)), C(self.__clean_code(code)))
        except subprocess.CalledProcessError:
            if self.enable_logging:
                print(f"couldn't preprocess {code}", file=sys.stderr)
            return None

    def __compile_with(
        self,
        compilers: tuple[Compiler, ...],
        datapoint: DataPoint,
        optimization_levels: tuple[int, ...],
    ) -> DataPoint | None:
        try:
            for compiler in compilers:
                for opt_level in optimization_levels:
                    datapoint.asm.append(compiler.compile(datapoint.c_code, opt_level))
        except CompilationError as _:
            if self.enable_logging:
                print(f"couldn't compile: {'*'*50} \n{datapoint.c_code}")
            return None
        else:
            return datapoint

    def take(
        self,
        n: int,
        compilers: tuple[Compiler, ...] = (GCC(), Clang()),
        optimization_levels: tuple[int, ...] = (0, 1, 2, 3),
    ) -> list[DataPoint]:
        taken: list[DataPoint] = []

        with ThreadPoolExecutor() as executor:
            while len(taken) != n:
                dataset_slice = list(islice(self.rows, n - len(taken)))
                if len(dataset_slice) == 0:
                    break
                preprocessed = [
                    dp
                    for dp in executor.map(
                        self.__datapoint_from_row,
                        dataset_slice,
                    )
                    if dp is not None
                ]

                compiled = [
                    dp
                    for dp in executor.map(
                        lambda dp: self.__compile_with(
                            compilers,
                            dp,
                            optimization_levels,
                        ),
                        preprocessed,
                    )
                    if dp is not None
                ]

                taken.extend(compiled)

        return taken
