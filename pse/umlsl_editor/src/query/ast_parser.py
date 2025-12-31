from pse.umlsl_editor.src.query.ast import ASTNode, ConjunctionNode, TrueNode, DisjunctionNode, NegationNode
from pse.umlsl_editor.src.query.token import Token, TokenType


def parse_binary(left: ASTNode, token: Token, right: ASTNode) -> ASTNode:
    match token.type:
        case TokenType.AND:
            return ConjunctionNode(left, right)
        case TokenType.OR:
            return DisjunctionNode(left, right)
        case _:
            raise SyntaxError(f"Unknown binary operator {token.type}")


class ASTParser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens

    def parse_ast(self):
        if not self.tokens:
            raise SyntaxError("Empty token list")
        return self.parse_ast_rec(0, len(self.tokens) - 1)

    def parse_ast_rec(self, start: int, end: int) -> ASTNode:
        if start > end:
            raise SyntaxError("Unexpected end of expression")

        tokens = self.tokens

        height = 0
        split_index = -1
        min_precedence = float('inf')

        # TODO: Incomplete
        precedence_map = {
            TokenType.OR: 1,
            TokenType.AND: 2
        }

        for i in range(start, end + 1):
            token = self.tokens[i]

            if token.type.left_bracket():
                height += 1
            elif token.type.right_bracket():
                height -= 1
            elif height == 0 and token.type in precedence_map:
                precedence = precedence_map[token.type]
                # Find the operator with the lowest binding (left-associativity)
                if precedence <= min_precedence:
                    min_precedence = precedence
                    split_index = i

        if height != 0:
            raise SyntaxError("Unbalanced parentheses: missing closing ')' or '}'")

        if split_index != -1:
            left_ast = self.parse_ast_rec(start, split_index - 1)
            token = tokens[split_index]
            right_ast = self.parse_ast_rec(split_index + 1, end)
            return parse_binary(left_ast, token, right_ast)

        if tokens[start].type.left_bracket() and tokens[end].type.right_bracket():
            return self.parse_ast_rec(start + 1, end - 1)

        return self.parse_expression(start, end)

    def parse_expression(self, start: int, end: int) -> ASTNode:
        token = self.tokens[start]

        # Parser unary tokens (has one operand)
        if token.type == TokenType.NEGATION:
            if start == end:
                raise SyntaxError("Negation operator requires an operand")
            operand = self.parse_ast_rec(start + 1, end)
            return NegationNode(operand)

        # Ensure we are looking at a single token
        if start == end:
            if token.type == TokenType.LITERAL:
                if token.value == "True":
                    return TrueNode()

        raise SyntaxError(f"Unexpected token or format at {start}: {token}")
