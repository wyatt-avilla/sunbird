from __future__ import annotations

from compile import generate_assembly_for_code_pairs
from data_parsing import read_data_csv

if __name__ == "__main__":
    parsed: list[tuple[str, int]] = read_data_csv("dataset/train.csv")
    new_data: list[tuple[str, int, str]] = generate_assembly_for_code_pairs(parsed)
