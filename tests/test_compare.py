import unittest
from scenecheck.analyzer import compare_script


class CompareScriptTests(unittest.TestCase):
    def test_overlap_and_missing_words(self):
        result = compare_script("The cat sat on mat", "The cat sat")
        self.assertEqual(result["unique_word_overlap"], 60.0)
        self.assertIn("on", result["words_in_script_not_heard"])
        self.assertIn("mat", result["words_in_script_not_heard"])

    def test_empty_script_is_safe(self):
        result = compare_script("", "hello world")
        self.assertEqual(result["unique_word_overlap"], 0.0)


if __name__ == "__main__":
    unittest.main()
