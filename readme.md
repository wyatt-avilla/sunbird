# sunbird 🐦‍🔥

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![python](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![pytorch](https://img.shields.io/badge/PyTorch-2.4.1-EE4C2C.svg?style=flat&logo=pytorch)](https://pytorch.org)
![Tree Sitter](https://img.shields.io/badge/tree_sitter-0.23.0-7E8F31)

## Overview

This project focuses on translating x86-64 assembly back into C code using a
machine learning model trained on a dataset of C code snippets. Each snippet is
compiled with multiple optimization levels across different compilers, and the
resulting assembly code is tokenized for use in training.

## Dataset

- the model was trained on an augmented version of
  [this dataset](https://www.kaggle.com/datasets/shirshaka/c-code-snippets-and-their-labels)
- each snippet of C code was compiled with the first four optimization levels of
  GCC and Clang, yielding 8 unique assembly code snippets for each element in
  the initial dataset (totaling 2.5 million snippets)

If `kaggle` is in your path, the original dataset can be downloaded with:

```sh
kaggle datasets download -d shirshaka/c-code-snippets-and-their-labels && \
unzip -d dataset c-code-snippets-and-their-labels.zip
```

### Generation

- compilation settings, including optimization levels and compiler choices are
  specified in `generate_data.py`
- the exact flags passed into the compilation subprocesses are specified in the
  `.compile()` methods in `compilation.py`

Compilation can be performed as follows:

```sh
./generate_data.py <filename.csv>
```

This will write a serialized list of `DataPoint` classes to
`filename_compiled.pkl`. Each `DataPoint` contains the original C code, its
corresponding assembly snippets, and associated metadata.

## Tokenization

C and assembly code snippets are tokenized semantically using the tree-sitter
library. Each token includes raw text paired with its symbolic identity, e.g.,
`(variable, 42)`.
