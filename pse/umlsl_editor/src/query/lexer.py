import re
from abc import ABC, abstractmethod
from enum import Enum


class TokenType(Enum):
    L_PAREN = "("
    R_PAREN = ")"
    L_CURLY = "{"
    R_CURLY = "}"
    COLON = ":"
    LESS_THAN = "<"
    GREATER_THAN = ">"
    H_CHOP = "\\hchop"
    V_CHOP = "\\vchop"
    CLAIM = "\\cl"
    CROSSING = "\\cs"
    RESERVE = "\\re"
    CAR_EQUALS = "="
    FREE = "\\free"
    AND = "\\and"
    OR = "\\or"
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

    @property
    def is_quantor_op(self):
        return self in _QUANTOR_OPS

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
    TokenType.EXITS,
    TokenType.FORALL
}
_QUANTOR_OPS = {
    TokenType.EXITS,
    TokenType.FORALL
}
_INFIX_BINARY_OPS_PRECEDENCE = {
    TokenType.AND: 2,
    TokenType.OR: 1,
    TokenType.CAR_EQUALS: 3  # irrelevant since equality requires parameters to be cars ({and, or} return booleans)
}


class Token(ABC):
    def __init__(self, type: TokenType, start_index: int, end_index: int):
        self.type = type
        self.start_index = start_index
        self.end_index = end_index

    @abstractmethod
    def value(self) -> str | None:
        pass


class SimpleToken(Token):
    def value(self) -> None:
        return None

    def __str__(self):
        return f"{self.type.name}"


class Literal(Token):
    def __init__(self, literal_value: str, start_index: int = 0, end_index: int = 0):
        super().__init__(TokenType.LITERAL, start_index, end_index)
        self._literal_value = literal_value

    def value(self) -> str:
        return self._literal_value

    def __str__(self):
        return f"{self.type.name}('{self._literal_value}')"


class Lexer:
    def __init__(self, text: str):
        self._input = text

    def tokenize(self) -> list[Token]:
        input = self._input

        token_patterns = []
        for t in TokenType:
            if t is not TokenType.LITERAL:
                pattern = f"(?P<{t.name}>{re.escape(t.value)})"
                token_patterns.append(pattern)

        master_pattern = re.compile("|".join(token_patterns))

        tokens = []
        last_pos = 0

        for match in master_pattern.finditer(input):
            start = match.start()
            if start > last_pos:
                literal_start = last_pos
                literal_end = match.start()
                literal_text = input[literal_start:literal_end].strip()

                if len(literal_text) != 0 and literal_text != " ":
                    tokens.append(Literal(literal_text, literal_start, literal_end))

            kind = match.lastgroup
            value = match.group()
            end = match.end()
            tokens.append(SimpleToken(TokenType[kind], start, start + len(value)))

            last_pos = end

        if last_pos < len(input):
            literal_text = input[last_pos:].strip()
            if len(literal_text) != 0 and literal_text != " ":
                tokens.append(Literal(literal_text, last_pos, len(input)))

        return tokens
