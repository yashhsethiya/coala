import sys
import unittest

sys.path.insert(0, ".")
from coalib.parsing.StringProcessing import InBetweenMatch, Match


class InBetweenMatchTest(unittest.TestCase):
    def test_properties(self):
        uut = InBetweenMatch(Match("ABC", 0), Match("DEF", 3), Match("GHI", 6))

        self.assertEqual(str(uut.begin), "ABC")
        self.assertEqual(uut.begin.position, 0)
        self.assertEqual(str(uut.inside), "DEF")
        self.assertEqual(uut.inside.position, 3)
        self.assertEqual(str(uut.end), "GHI")
        self.assertEqual(uut.end.position, 6)


if __name__ == '__main__':
    unittest.main(verbosity=2)
