import re
from abc import ABC, abstractmethod
from enum import Enum


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
    def is_atom_op(self):
        return self in _ATOM_OPS

    def get_infix_binary_op_precedence(self):
        if not self.is_infix_binary_op:
            raise ValueError(f"Token {self} is not an infix binary operation.")
        return _INFIX_BINARY_OPS_PRECEDENCE[self]


_ATOM_OPS = {
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


class Token(ABC):
    def __init__(self, type: TokenType):
        self.type = type

    @abstractmethod
    def value(self) -> str | None:
        pass


class SimpleToken(Token):
    def value(self) -> None:
        return None

    def __str__(self):
        return f"{self.type.name}"


class Literal(Token):
    def __init__(self, literal_value: str):
        super().__init__(TokenType.LITERAL)
        self.literal_value = literal_value

    def value(self) -> str:
        return self.literal_value

    def __str__(self):
        return f"{self.type.name}('{self.literal_value}')"


class Lexer:
    def __init__(self, text: str):
        self.text = text

    def tokenize(self) -> list[Token]:
        # Remove whitespace and tabs
        text = self.text.replace(" ", "").replace("\t", "")

        token_patterns = []
        for t in TokenType:
            if t is not TokenType.LITERAL:
                pattern = f"(?P<{t.name}>{re.escape(t.value)})"
                token_patterns.append(pattern)

        master_pattern = re.compile("|".join(token_patterns))

        tokens = []
        last_pos = 0

        for match in master_pattern.finditer(text):
            if match.start() > last_pos:
                literal_text = text[last_pos:match.start()]
                tokens.append(Literal(literal_text))

            kind = match.lastgroup
            value = match.group()
            # todo: value should be token_type?
            tokens.append(SimpleToken(TokenType[kind]))

            last_pos = match.end()

        if last_pos < len(text):
            tokens.append(Literal(text[last_pos:]))

        return tokens
