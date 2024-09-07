from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor

from compilers import GCC, Assembly, Clang, CompilationError, Compiler
from data_parsing import DataPoint, read_data_csv


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
    parsed: list[DataPoint] = read_data_csv("dataset/sample.csv")
    compiled: list[DataPoint] = compile_with([GCC(), Clang()], parsed, [0, 1, 2, 3])

    print(len(compiled))
    print(f"{len(parsed) - len(compiled)} failed compilations")
