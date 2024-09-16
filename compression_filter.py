from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Generator

from tree_sitter import Parser, Tree
from tree_sitter_language_pack import get_language

if TYPE_CHECKING:
    from compilation import Code
    from datapoint import DataPoint


class CompressionFilter:
    def __init__(self, dp: DataPoint) -> None:
        self.dp = dp

    def __ast_leaf_iterator(self, code: Code) -> Generator[tuple[str, str], None, None]:
        parser: Parser = Parser()
        parser.language = get_language(code.ts_language)
        tree: Tree = parser.parse(code.source.encode("utf-8"))
        cursor = tree.walk()

        visited_children = False
        while True:
            if (node := cursor.node) is None:
                break

            if not visited_children:
                if node.child_count == 0 and node.text is not None:
                    yield (node.type, node.text.decode("utf-8"))
                if not cursor.goto_first_child():
                    visited_children = True
            elif cursor.goto_next_sibling():
                visited_children = False
            elif not cursor.goto_parent():
                break

    def all_tokens(self) -> list[tuple[list[tuple[str, str]], list[tuple[str, str]]]]:
        results = []

        ignore_types: set[str] = {"meta_ident", "ERROR"}
        asm_to_c_types: dict[str, str] = {
            "int": "number_literal",
            "string": "string_content",
        }
        simplification_map: dict[str, dict[str, str]] = {
            "identifier": defaultdict(
                lambda: f"identifier_{len(simplification_map['identifier'])}",
            ),
            "number_literal": defaultdict(
                lambda: f"number_literal_{len(simplification_map['number_literal'])}",
            ),
            "string_content": defaultdict(
                lambda: f"string_content_{len(simplification_map['string_content'])}",
            ),
        }

        compressed_c_tokens: list[tuple[str, str]] = [
            (typ, simplification_map[typ][txt])
            if typ in simplification_map
            else (typ, txt)
            for (typ, txt) in self.__ast_leaf_iterator(self.dp.c_code)
        ]

        for asm in self.dp.asm:
            compressed_asm_tokens = [
                (typ, simplification_map[asm_to_c_types[typ]][txt])
                if typ in asm_to_c_types
                else (typ, txt)
                for (typ, txt) in self.__ast_leaf_iterator(asm)
            ]
            results.append(
                (
                    list(
                        filter(
                            lambda pair: pair[0] not in ignore_types,
                            compressed_asm_tokens,
                        ),
                    ),
                    compressed_c_tokens,
                ),
            )

        return results
