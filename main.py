from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from compilers import GCC, CompilationError
from data_parsing import DataPoint, read_data_csv


def compile_with_gcc(
    datapoints: list[DataPoint],
) -> list[DataPoint]:
    result: list[DataPoint] = []

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(GCC().compile, datapoint.c_code) for datapoint in datapoints
        ]

        for future, datapoint in zip(futures, datapoints):
            try:
                assembly_code = future.result()
                datapoint.asm.append(assembly_code)  # invalid type for time being
                result.append(datapoint)
            except CompilationError as e:
                print(f"Failed to build: {"*"*40} \n\n{datapoint.c_code}\n\n")
                print(f"Console Output: {e.console_output}")
                continue

    return result


if __name__ == "__main__":
    parsed: list[DataPoint] = read_data_csv("dataset/sample.csv")
    compiled: list[DataPoint] = compile_with_gcc(parsed)

    print(f"{len(compiled)} vs {len(parsed)}")
