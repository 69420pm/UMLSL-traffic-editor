import unittest

from pse.umlsl_editor.src.query.ast_parser import ASTParser
from pse.umlsl_editor.src.query.token import Lexer


class TestQuery(unittest.TestCase):

    def test_tokenizer(self):
        query = "\\(True \\and{\\neg True}\\) \\or \\({True}\\and{True}\\)"
        tokens = Lexer(query).tokenize()

        for index, token in enumerate(tokens):
            print(f"{index}: {token}")
        ast = ASTParser(tokens).parse_ast()

        assert True
