import re
from enum import Enum
from typing import Optional


class TokenType(Enum):
    AND = "\\and"
    OR = "\\or"
    NOT = "\\not"
    H_CHOP = "\\hchop"
    V_CHOP = "\\vchop"
    L_PAREN = "\\("
    R_PAREN = "\\)"
    NEGATION = "\\neg"
    EXITS = "\\"
    TOP = "^"
    DOWN = "_"
    L_CURLY = "{"
    R_CURLY = "}"
    LITERAL = "LITERAL"  # placeholder

    def exact_match(self) -> Optional[str]:
        if self == TokenType.LITERAL:
            return None
        return self.name

    def left_bracket(self):
        return self == TokenType.L_PAREN or self == TokenType.L_CURLY

    def right_bracket(self):
        return self == TokenType.R_PAREN or self == TokenType.R_CURLY


class Token:
    def __init__(self, type: TokenType, value: str):
        self.type = type
        self.value = value

    def __str__(self):
        if self.type == TokenType.LITERAL:
            return f"{self.type}('{self.value}')"
        else:
            return f"{self.type}"


class Lexer:
    def __init__(self, text: str):
        self.text = text

    def tokenize(self) -> list[Token]:
        # Remove whitespace and tabs
        text = self.text.replace(" ", "").replace("\t", "")

        token_patterns = []
        for t in TokenType:
            if t.exact_match():
                pattern = f"(?P<{t.name}>{re.escape(t.value)})"
                token_patterns.append(pattern)

        master_pattern = re.compile("|".join(token_patterns))

        tokens = []
        last_pos = 0

        for match in master_pattern.finditer(text):
            if match.start() > last_pos:
                literal_text = text[last_pos:match.start()]
                tokens.append(Token(TokenType.LITERAL, literal_text))

            kind = match.lastgroup
            value = match.group()
            tokens.append(Token(TokenType[kind], value))

            last_pos = match.end()

        if last_pos < len(text):
            tokens.append(Token(TokenType.LITERAL, text[last_pos:]))

        return tokens

