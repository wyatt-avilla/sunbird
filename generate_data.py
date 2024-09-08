from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor

from compilation import GCC, Assembly, Clang, CompilationError, Compiler
from data import DataPoint, read_data_csv, write_data_csv


def compile_with(
    compilers: list[Compiler],
    datapoints: list[DataPoint],
    optimization_levels: list[int],
) -> list[DataPoint]:
    compiled: set[DataPoint] = set()

    with ThreadPoolExecutor() as executor:
        futures: list[tuple[DataPoint, Future]] = [
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
            print(f"Failed to build: {"*"*70} \n\n{datapoint.c_code}\n\n")
            print(f"Console Output: {e.console_output}")
            continue

    return compiled


if __name__ == "__main__":
    input_csv_name: str = "dataset/sample.csv"
    compilers: list[Compiler] = [GCC(), Clang()]
    optimization_levels: list[int] = [0, 1, 2, 3]

    c_code: list[DataPoint] = read_data_csv(input_csv_name)
    compiled: list[DataPoint] = compile_with(compilers, c_code, optimization_levels)
    write_data_csv(
        input_csv_name.replace(".csv", "_compiled.csv"),
        [datapoint.as_dict() for datapoint in compiled],
    )
