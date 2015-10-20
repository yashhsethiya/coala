import sys
import unittest

sys.path.insert(0, ".")
from coalib.tests.parsing.StringProcessing.StringProcessingTestBase import (
    StringProcessingTestBase)
from coalib.parsing.StringProcessing import unescaped_split


class UnescapedSplitTest(StringProcessingTestBase):
    bs = StringProcessingTestBase.bs

    test_basic_pattern = "'"
    test_basic_expected_results = [
        ["out1 ", r"escaped-escape:        \\ ", " out2"],
        ["out1 ", r"escaped-quote:         \' ", " out2"],
        ["out1 ", r"escaped-anything:      \X ", " out2"],
        ["out1 ", r"two escaped escapes: \\\\ ", " out2"],
        ["out1 ", r"escaped-quote at end:   \'", " out2"],
        ["out1 ", "escaped-escape at end:  " + 2 * bs, " out2"],
        ["out1           ", "str1", " out2 ", "str2", " out2"],
        [r"out1 \'        ", "str1", " out2 ", "str2", " out2"],
        [r"out1 \\\'      ", "str1", " out2 ", "str2", " out2"],
        [r"out1 \\        ", "str1", " out2 ", "str2", " out2"],
        [r"out1 \\\\      ", "str1", " out2 ", "str2", " out2"],
        ["out1         " + 2 * bs, "str1", " out2 ", "str2", " out2"],
        ["out1       " + 4 * bs, "str1", " out2 ", "str2", " out2"],
        ["out1           ", "str1", "", "str2", "", "str3", " out2"],
        [""],
        ["out1 out2 out3"],
        [bs],
        [2 * bs]]

    # Test the basic unescaped_split() functionality.
    def test_basic(self):
        split_pattern = self.test_basic_pattern
        expected_results = self.test_basic_expected_results

        self.assertResultsEqual(
            unescaped_split,
            {(split_pattern, test_string, 0, False, use_regex): result
             for test_string, result in zip(self.test_strings,
                                            expected_results)
             for use_regex in [True, False]},
            list)

    # Test the unescaped_split() function while varying the max_split
    # parameter.
    def test_max_split(self):
        split_pattern = self.test_basic_pattern
        expected_master_results = self.test_basic_expected_results

        for max_split in [1, 2, 3, 4, 5, 6, 7, 8, 9, 112]:
            expected_results = [
                elem[0 : max_split] for elem in expected_master_results]

            for res, master in zip(expected_results, expected_master_results):
                if max_split < len(master):
                    # max_split is less the length of our master result list,
                    # need to append the rest as a joined string.
                    res.append(str.join(split_pattern, master[max_split : ]))

            self.assertResultsEqual(
                unescaped_split,
                {(split_pattern,
                  test_string,
                  max_split,
                  False,
                  use_regex): result
                 for test_string, result in zip(self.test_strings,
                                                expected_results)
                 for use_regex in [True, False]},
                list)

    # Test the unescaped_split() function with different regex patterns.
    def test_regex_pattern(self):
        expected_results = [
            ["", "", r"cba###\\13q4ujsabbc\+'**'ac###.#.####-ba"],
            ["", "c", r"ccba###\\13q4ujs", r"bc\+'**'ac###.#.####-ba"],
            ["", "c", r"ccba###\\13q4ujs", r"bc\+'**'", "###.#.####-ba"],
            ["abcabccba###", r"\13q4ujsabbc", "+'**'ac###.#.####-ba"],
            ["abcabccba", r"\\13q4ujsabbc\+'**'ac", ".", ".", "-ba"],
            ["", "", "c", "", "cc", "", "", "", r"\13q4ujs", "", "",
                r"c\+'**'", "c", "", "", "", "", "-", "", ""],
            ["", r"cba###\\13q4ujs", r"\+'**'", "###.#.####-ba"],
            ["abcabccba###" + 2 * self.bs,
                r"3q4ujsabbc\+'**'ac###.#.####-ba"]]

        self.assertResultsEqual(
            unescaped_split,
            {(pattern, self.multi_pattern_test_string, 0, False, True): result
             for pattern, result in zip(self.multi_patterns,
                                        expected_results)},
            list)

    # Test the unescaped_split() function for its remove_empty_matches feature.
    def test_auto_trim(self):
        expected_results = [
            [],
            [2 * self.bs, r"\\\\\;\\#", r"\\\'", r"\;\\\\", "+ios"],
            ["1", "2", "3", "4", "5", "6"],
            ["1", "2", "3", "4", "5", "6", "7"],
            [],
            ["Hello world"],
            [r"\;"],
            [2 * self.bs],
            ["abc", "a", "asc"]]

        self.assertResultsEqual(
            unescaped_split,
            {(self.auto_trim_test_pattern,
              test_string,
              0,
              True,
              use_regex): result
             for test_string, result in zip(self.auto_trim_test_strings,
                                            expected_results)
             for use_regex in [True, False]},
            list)

    # Test the unescaped_split() function with regexes disabled.
    def test_disabled_regex(self):
        expected_results = [[x] for x in self.test_strings]

        self.assertResultsEqual(
            unescaped_split,
            {("'()", test_string, 0, False, False): result
             for test_string, result in zip(self.test_strings,
                                            expected_results)},
            list)


if __name__ == '__main__':
    unittest.main(verbosity=2)

