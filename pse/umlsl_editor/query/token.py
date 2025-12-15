from typing import List


class TokenType(Enum):
    ATOM = 1
    AND = 2
    OR = 3
    NOT = 4
    H_CHOP = 5
    V_CHOP = 6
    LPAREN = 7
    RPAREN = 8

class Token:
    def __init__(self, type_: TokenType, value: str):
        self.type = type_
        self.value = value

class Lexer:
    """Tokenizes LaTeX strings like '\land', '\lor', 're(c1)'."""
    def tokenize(self, source: str) -> List[Token]:
        pass