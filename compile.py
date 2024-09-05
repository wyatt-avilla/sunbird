from __future__ import annotations

import subprocess
from concurrent.futures import ThreadPoolExecutor


def generate_assembly(c_code: str) -> str:
    try:
        result = subprocess.run(
            [
                "gcc",
                "-x",
                "c",
                "-",
                "-S",
                "-o",
                "-",
            ],
            input=c_code.encode("utf-8"),
            check=True,
            capture_output=True,
        )
        assembly_code = result.stdout.decode("utf-8")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Compilation failed: {e.stderr.decode('utf-8')}") from e

    return assembly_code


def generate_assembly_for_code_pairs(
    code_pairs: list[tuple[str, int]],
) -> list[tuple[str, int, str]]:
    result = []

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(generate_assembly, c_code) for c_code, _ in code_pairs
        ]

        for future, (c_code, label) in zip(futures, code_pairs):
            try:
                assembly_code = future.result()
                result.append((c_code, label, assembly_code))
            except RuntimeError as e:
                print(f"Failed to build: \n\n{c_code}\n\nWith error: {e}")
                continue

    return result
