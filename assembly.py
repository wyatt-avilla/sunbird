from compilers import Compiler


class Assembly:
    def __init__(self, asm_code: str, compiler: Compiler) -> None:
        self.asm_code: str = asm_code
        self.compiler: Compiler = compiler
