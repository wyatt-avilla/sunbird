import subprocess


class CompilationError(Exception):
    def __init__(self, message: object, console_output: str) -> None:
        super().__init__(message)
        self.console_output = console_output

    def __str__(self) -> str:
        return super().__str__()


class Compiler:
    def __init__(self) -> None:
        pass

    def compile(self) -> None:
        msg: str = "Subclasses should implement this"
        raise NotImplementedError(msg)


class GCC(Compiler):
    def __init__(self) -> None:
        super().__init__()

    def compile(self, c_code: str) -> str:
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
            raise CompilationError(e, e.stderr.decode("utf-8")) from e

        return assembly_code


class Clang(Compiler):
    def __init__(self) -> None:
        super().__init__()

    def compile(self, c_code: str) -> str:
        try:
            result = subprocess.run(
                [
                    "clang",
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
            raise CompilationError(e, e.stderr.decode("utf-8")) from e

        return assembly_code
