from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor

from assembly import Assembly
from compilers import GCC, Clang, CompilationError, Compiler
from data_parsing import DataPoint, read_data_csv


def compile_with(
    compilers: list[Compiler],
    datapoints: list[DataPoint],
) -> list[DataPoint]:
    compiled: list[DataPoint] = []

    with ThreadPoolExecutor() as executor:
        futures: list[tuple[Future, Compiler]] = [
            (executor.submit(compiler.compile, datapoint.c_code), compiler)
            for compiler in compilers
            for datapoint in datapoints
        ]

    for (future, compiler), datapoint in zip(futures, datapoints):
        try:
            assembly_code = future.result()
            datapoint.asm.append(
                Assembly(assembly_code, compiler),
            )
            compiled.append(datapoint)
        except CompilationError as e:
            print(f"Failed to build: {"*"*70} \n\n{datapoint.c_code}\n\n")
            print(f"Console Output: {e.console_output}")
            continue

    return compiled


if __name__ == "__main__":
    parsed: list[DataPoint] = read_data_csv("dataset/sample.csv")
    compiled: list[DataPoint] = compile_with([GCC(), Clang()], parsed)

    print(f"{len(parsed) - len(compiled)} failed compilations")
