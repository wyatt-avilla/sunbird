#!/usr/bin/env python3

from __future__ import annotations

import pickle
import sys
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path

from compilation import GCC, Assembly, Clang, CompilationError, Compiler
from data import DataPoint, read_data_csv


def compile_with(
    compilers: tuple[Compiler, ...],
    datapoints: list[DataPoint],
    optimization_levels: tuple[int, ...],
) -> list[DataPoint]:
    compiled: set[DataPoint] = set()

    with ThreadPoolExecutor() as executor:
        futures: list[tuple[DataPoint, Future[Assembly]]] = [
            (datapoint, executor.submit(compiler.compile, datapoint.c_code, opt_level))
            for datapoint in datapoints
            for compiler in compilers
            for opt_level in optimization_levels
        ]

    for datapoint, future in futures:
        try:
            assembly_code: Assembly = future.result()
            datapoint.asm.append(assembly_code)
            compiled.add(datapoint)
        except CompilationError as e:
            print(f"Failed to build: {'*'*70} \n\n{datapoint.c_code}\n\n")
            print(f"Console Output: {e.console_output}")
            continue

    return list(compiled)


def openable(f_name: str) -> bool:
    opened: bool = False
    try:
        with Path(f_name).open("r") as _:
            pass
        opened = True
    except FileNotFoundError:
        print(f"{f_name} does not exist")
    except PermissionError:
        print(f"you don't have permission to access {f_name}")
    except IsADirectoryError:
        print("found a directory instead of a file")
    except OSError as e:
        print("an unexpected OS error occurred")
        print(e)

    return opened


def csv_to_pickle_compile(
    input_csv_name: str,
    compilers: tuple[Compiler, ...] = (GCC(), Clang()),
    optimization_levels: tuple[int, ...] = (0, 1, 2, 3),
) -> None:
    c_code: list[DataPoint] = read_data_csv(input_csv_name)
    compiled: list[DataPoint] = compile_with(compilers, c_code, optimization_levels)

    with Path(input_csv_name.replace(".csv", "_compiled.pkl")).open("wb") as file:
        pickle.dump(compiled, file)


if __name__ == "__main__":
    input_csv_name: str = sys.argv[1]

    if not openable(input_csv_name):
        sys.exit(1)

    if not input_csv_name.endswith(".csv"):
        print("expected a csv file")
        sys.exit(1)

    print(f"compiling content from {input_csv_name} ...")
    csv_to_pickle_compile(input_csv_name)
