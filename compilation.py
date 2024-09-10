from __future__ import annotations

import subprocess
from typing import Generator

from tree_sitter import Node, Parser
from tree_sitter_language_pack import get_language


class CompilationError(Exception):
    def __init__(self, message: object, console_output: str) -> None:
        super().__init__(message)
        self.console_output = console_output

    def __str__(self) -> str:
        return super().__str__()


class VersionParseError(Exception):
    def __init__(self, message: object, console_output: str) -> None:
        super().__init__(message)
        self.console_output = console_output

    def __str__(self) -> str:
        return super().__str__()


class Code:
    def __init__(self, source: str) -> None:  # noqa: ARG002
        self.unimplemented_error: str = "Subclasses should implement this"

    def __str__(self) -> str:
        return self.source

    def as_tokens(self) -> Generator[Node, None, None]:
        tree = self.parser.parse(self.source.encode("utf-8"))
        cursor = tree.walk()

        visited_children = False
        while True:
            if not visited_children:
                if cursor.node.child_count == 0:
                    yield (cursor.node.type, cursor.node.text.decode("utf-8"))
                if not cursor.goto_first_child():
                    visited_children = True
            elif cursor.goto_next_sibling():
                visited_children = False
            elif not cursor.goto_parent():
                break


class C(Code):
    def __init__(self, source: str) -> None:
        self.source: str = source
        self.parser: Parser = Parser()
        self.parser.language = get_language("c")


class Assembly(Code):
    def __init__(
        self,
        source: str,
        compiler: Compiler,
        optimization_level: int,
    ) -> None:
        self.source: str = source
        self.compiler: Compiler = compiler
        self.optimization_level: int = optimization_level
        self.parser: Parser = Parser()
        self.parser.language = get_language("asm")


class Compiler:
    def __init__(self) -> None:
        self.unimplemented_error: str = "Subclasses should implement this"

    def get_version(self) -> str:
        raise NotImplementedError(self.unimplemented_error)

    def compile(self, optimization_level: int = 0) -> Assembly:
        raise NotImplementedError(self.unimplemented_error)


class GCC(Compiler):
    def __init__(self) -> None:
        super().__init__()

    def get_version(self) -> str:
        try:
            result = subprocess.run(
                [
                    "gcc",
                    "-dumpfullversion",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            version = result.stdout
        except subprocess.CalledProcessError as e:
            raise VersionParseError(e, e.stderr) from e

        return version.strip()

    def compile(self, c_code: C, optimization_level: int = 0) -> Assembly:
        try:
            result = subprocess.run(
                [
                    "gcc",
                    f"-O{optimization_level}",
                    "-fno-verbose-asm",
                    "-masm=intel",
                    "-x",
                    "c",
                    "-",
                    "-S",
                    "-o",
                    "-",
                ],
                input=c_code.source.encode("utf-8"),
                check=True,
                capture_output=True,
            )
            assembly_code = result.stdout.decode("utf-8")
        except subprocess.CalledProcessError as e:
            raise CompilationError(e, e.stderr.decode("utf-8")) from e

        return Assembly(assembly_code, self, optimization_level)


class Clang(Compiler):
    def __init__(self) -> None:
        super().__init__()

    def get_version(self) -> str:
        try:
            result = subprocess.run(
                [
                    "clang",
                    "--version",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            version = result.stdout
        except subprocess.CalledProcessError as e:
            raise VersionParseError(e, e.stderr) from e

        return version.splitlines()[0].replace("clang version", "").strip()

    def compile(self, c_code: C, optimization_level: int = 0) -> Assembly:
        try:
            result = subprocess.run(
                [
                    "clang",
                    f"-O{optimization_level}",
                    "-fno-verbose-asm",
                    "-masm=intel",
                    "-x",
                    "c",
                    "-",
                    "-S",
                    "-o",
                    "-",
                ],
                input=c_code.source.encode("utf-8"),
                check=True,
                capture_output=True,
            )
            assembly_code = result.stdout.decode("utf-8")
        except subprocess.CalledProcessError as e:
            raise CompilationError(e, e.stderr.decode("utf-8")) from e

        return Assembly(assembly_code, self, optimization_level)
