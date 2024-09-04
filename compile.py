from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


def generate_assembly(c_code: str) -> str:
    with tempfile.NamedTemporaryFile(suffix=".c", delete=False) as c_file:
        c_file.write(c_code.encode("utf-8"))
        c_file.flush()
        temp_c_path = c_file.name

    try:
        with tempfile.NamedTemporaryFile(suffix=".s", delete=False) as asm_file:
            temp_asm_path = asm_file.name

        subprocess.run(
            ["gcc", "-S", temp_c_path, "-o", temp_asm_path],
            check=True,
            capture_output=False,
        )

        with Path.open(temp_asm_path, "r") as f:
            assembly_code = f.read()
    finally:
        Path.unlink(temp_c_path, missing_ok=True)
        Path.unlink(temp_asm_path, missing_ok=True)

    return assembly_code


def generate_assembly_for_code_pairs(
    code_pairs: list[tuple[str, int]],
) -> list[tuple[str, int, str]]:
    result = []
    for c_code, label in code_pairs:
        try:
            assembly_code = generate_assembly(c_code)
        except subprocess.CalledProcessError as e:
            print(f"failed to build: \n\n {c_code}")
            print(f"\n with error {e}")

        result.append((c_code, label, assembly_code))
    return result
