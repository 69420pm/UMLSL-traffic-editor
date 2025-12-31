from typing import List

from pse.umlsl_editor.src.query.ast import ASTNode
from pse.umlsl_editor.src.query.token import Token


class Parser:
    """Recursive descent query."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def parse(self) -> ASTNode:
        pass

    def parse_expression(self) -> ASTNode:
        pass

    def parse_term(self) -> ASTNode:
        pass
