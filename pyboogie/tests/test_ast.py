""" 
Tests for basing Boogie parsing and AST building.
These tests focus on the core subset of boogie supported.
"""
from unittest import TestCase
from ..grammar import BoogieParser
from ..ast import parseAst, parseExprAst, AstProgram, AstImplementation,\
    AstBody, AstBinding, AstIntType, AstAssignment, AstId, AstBinExpr, AstNumber, replace
from pyparsing import ParseException

class TestAst(TestCase):
    testProgs = [
        (
            """
                implementation main() {
                }
            """,
            AstProgram([AstImplementation("main", [], [], AstBody([], []))])
        ),
        (
            """
                implementation main() {
                    var x: int;
                }
            """,
            AstProgram([
                AstImplementation("main", [], [],
                    AstBody([AstBinding(["x"], AstIntType())], []))])
        ),
        (
            """
                implementation main() {
                    var x: int;
                    x := x+42;
                }
            """,
            AstProgram([
                AstImplementation("main", [], [],
                    AstBody([AstBinding(["x"], AstIntType())],
                    [AstAssignment(AstId('x'), AstBinExpr(AstId("x"), "+", AstNumber(42)))]))])
        ),

    ]
    def test_bad_parse(self):
        """ Make sure parseAst doesn't fail silently
        """
        badProgs = [
            "foo",
            "implementation main ()",
            "implementation main () {",
            "implementation main () returns () {}",
            """implementation main () returns () {
                a:= 1
            }""",
        ]
        for text in badProgs:
            with self.assertRaises(ParseException):
                parseAst("badProgs")

    def test_parse(self):
        """ For each pair of text S and expected parse tree T in
            TestAst.testProgs check parseAst(S) == T
        """
        for (text, expectedAst) in self.testProgs:
            root = parseAst(text)
            assert (root == expectedAst), "Expected: \n{} instead got \n{} from raw text \n{}"\
                .format(str(expectedAst), str(root), text)

    def test_roundtrip(self):
        "For each parse tree T in TestAst.testProgs check parseAst(str(T)) == T"
        for (_, expected) in self.testProgs:
            try:
                got = parseAst(str(expected))
                assert (expected == got), "Pretty-printed and parsed tree {} differs from original {}"\
                    .format(str(got), str(expected))
            except:
                print ("Failed parsing {}".format(str(expected)))
                raise

    def test_replace(self):
        "Check that replace() function works correctly"
        tests = [
            ("x+y", {AstId('x'): AstNumber(42)}, "(42+y)"),
            ("x+y", {AstId('z'): AstNumber(42)}, "(x+y)"),
            ("x+(y+z)", {AstId('y'): AstNumber(42), parseExprAst('y+z'): AstNumber(43)}, "(x+43)"),
        ]
        for (expr, replM, expected) in tests:
            origExpr = parseExprAst(expr) if (isinstance(expr, str)) else expr
            replacedExp = replace(origExpr, replM)
            expectedExpr = parseExprAst(expected) if (isinstance(expected, str)) else expected
            assert (replacedExp == expectedExpr),\
                "Bad replace: Expected {} got {}".format(expected, replacedExp)