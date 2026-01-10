import re
from enum import Enum
from typing import Optional


class TokenType(Enum):
    L_PAREN = "("
    R_PAREN = ")"
    L_CURLY = "{"
    R_CURLY = "}"
    LESS_THAN = "<"
    GREATER_THAN = ">"
    H_CHOP = "\\hchop"
    V_CHOP = "\\vchop"
    CLAIM = "\\cl"
    CROSSING = "\\cs"
    RESERVE = "\\re"
    CAR_EQUALS = "="
    FREE = "\\free"
    AND = "and"
    OR = "or"
    NEGATION = "\\neg"
    NEGATION_SHORT = "!"
    EXITS = "\\exists"
    FORALL = "\\forall"
    TRUE = "true"
    LITERAL = "LITERAL"  # value "LITERAL" is a placeholder

    def exact_match(self) -> Optional[str]:
        if self == TokenType.LITERAL:
            return None
        return self.name

    @property
    def is_infix_binary_op(self):
        return self in _INFIX_BINARY_OPS

    @property
    def is_prefix_binary_op(self):
        return self in _PREFIX_BINARY_OPS

    @property
    def is_binary_op(self):
        return self.is_infix_binary_op or self.is_prefix_binary_op

    @property
    def is_unary_op(self):
        return self in _UNARY_OPS

    @property
    def is_nullary_op(self):
        return self in _NULLARY_OPS

    def get_infix_binary_op_precedence(self):
        if not self.is_infix_binary_op:
            raise ValueError(f"Token {self} is not an infix binary operation.")
        return _INFIX_BINARY_OPS_PRECEDENCE[self]


_NULLARY_OPS = {
    TokenType.TRUE,
    TokenType.FREE,
    TokenType.CROSSING
}
_UNARY_OPS = {
    TokenType.NEGATION,
    TokenType.NEGATION_SHORT,
    TokenType.CLAIM,
    TokenType.RESERVE,
    TokenType.EXITS,
    TokenType.FORALL
}

### For tokens that correspond to operations and require 2 parameters, we specify whether they are infix ({p1} op {p2}) or
### prefix (op {p1}{p2})
_INFIX_BINARY_OPS = {
    TokenType.AND,
    TokenType.OR,
    TokenType.CAR_EQUALS
}
_PREFIX_BINARY_OPS = {
    TokenType.H_CHOP,
    TokenType.V_CHOP,
}
_INFIX_BINARY_OPS_PRECEDENCE = {
    TokenType.AND: 2,
    TokenType.OR: 1,
    TokenType.CAR_EQUALS: 3  # irrelevant since equality requires parameters to be cars ({and, or} return booleans)
}


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
