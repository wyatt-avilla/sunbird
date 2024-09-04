#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path


def calculate_sha256(f_name: Path, chunk_size: int = 8192) -> str:
    sha256 = hashlib.sha256()
    with f_name.open("rb") as f:
        while chunk := f.read(chunk_size):
            sha256.update(chunk)

    return sha256.hexdigest()


def verify_dataset(data_dir: str = "dataset") -> None:
    chksm_map: dict[str, str] = {
        "train.csv": "477e5e323ff731761a8e72722daa112c4a3c93dba2af7de430c7d222f3417455",
        "test.csv": "ef6bfd2bccaf08e0295bbaac0ba7e0b3c78620e5109256900b3e27813e43bb86",
    }

    for f_name in chksm_map:
        path: Path = Path(f"{data_dir}/{f_name}")
        if not path.is_file():
            print(f"{f_name} not found.")
            sys.exit(1)

        if calculate_sha256(path) != chksm_map[f_name]:
            print(f"{f_name} didn't match checksum.")
            sys.exit(1)

    print("Dataset present.")


def get_installed_packages() -> set[str]:
    result = subprocess.run(
        ["pip", "freeze"],
        capture_output=True,
        text=True,
        check=False,
    )
    return {line.split("==")[0].lower() for line in result.stdout.splitlines()}


def check_requirements(requirements_file: str = "reqs.txt") -> None:
    with Path.open(requirements_file, "r") as file:
        requirements = file.read().splitlines()

    required_packages = {
        requirement.split("==")[0].lower()
        for requirement in requirements
        if requirement.strip() and not requirement.startswith("#")
    }
    installed_packages = get_installed_packages()

    missing_packages = required_packages - installed_packages

    if missing_packages:
        print("Missing packages:")
        for pkg in missing_packages:
            print(f"- {pkg}")
        sys.exit(1)
    else:
        print("All dependencies are satisfied.")


if __name__ == "__main__":
    check_requirements()
    verify_dataset()
