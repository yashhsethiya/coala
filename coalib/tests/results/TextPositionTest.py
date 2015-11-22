import sys
import unittest

sys.path.insert(0, ".")
from coalib.results.TextPosition import TextPosition


class TextPositionTest(unittest.TestCase):
    def test_fail_instantation(self):
        with self.assertRaises(ValueError):
            SourcePosition(None, 2)

        with self.assertRaises(TypeError):
            SourcePosition("hello", 3)

        with self.assertRaises(TypeError):
            SourcePosition(4, "world")

        with self.assertRaises(TypeError):
            SourcePosition("double", "string")

    def test_properties(self):
        uut = SourcePosition(None, None)
        self.assertEqual(uut.line, None)
        self.assertEqual(uut.column, None)

        SourcePosition(7, None)
        self.assertEqual(uut.line, 7)
        self.assertEqual(uut.column, None)

        SourcePosition(8, 39)
        self.assertEqual(uut.line, 8)
        self.assertEqual(uut.column, 39)


if __name__ == '__main__':
    unittest.main(verbosity=2)
