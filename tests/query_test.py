import unittest

from pse.umlsl_editor.src.query.ast.ast_parser import ASTParser
from pse.umlsl_editor.src.query.lexer import Lexer


class TestQuery(unittest.TestCase):

    def test_tokenizer(self):
        query = "\\(True \\and{\\neg True}\\) \\or \\({True}\\and{True}\\)"
        tokens = Lexer(query).tokenize()

        for index, token in enumerate(tokens):
            print(f"{index}: {token}")
        ast = ASTParser(tokens).parse_ast()

        assert True

    def test_compute_latex_invalid(self):
        from unittest.mock import Mock
        from pse.umlsl_editor.src.query.evaluator import UMLSLEvaluator, ParserError

        evaluator = UMLSLEvaluator(Mock())
        with self.assertRaises(ParserError):
            evaluator.compute_latex("invalid")
