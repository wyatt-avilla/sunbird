import subprocess


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


class Compiler:
    def __init__(self) -> None:
        self.unimplemented_error: str = "Subclasses should implement this"

    def get_version(self) -> str:
        raise NotImplementedError(self.unimplemented_error)

    def compile(self) -> None:
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
