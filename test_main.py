import pytest
from collections import defaultdict
from unittest.mock import patch, mock_open
from main import clean_poem, create_ngrams, create_line, save_poem, prompt_seed_word


# ─────────────────────────────────────────────
# clean_poem
# ─────────────────────────────────────────────

class TestCleanPoem:

    def test_adds_period_when_no_ending_punctuation(self):
        result = clean_poem("the river moves")
        assert result.endswith(".")

    def test_does_not_add_period_when_already_punctuated(self):
        for ending in ["the river moves.", "the river moves!", "the river moves?"]:
            result = clean_poem(ending)
            assert not result.endswith("..")
            assert result[-1] in ".!?"

    def test_corrects_lowercase_i(self):
        result = clean_poem("i saw the moon and i wept")
        assert " i " not in result
        assert result.startswith("I")

    def test_does_not_alter_words_containing_i(self):
        result = clean_poem("inside the iris bloomed")
        assert "inside" in result
        assert "iris" in result

    def test_collapses_multiple_spaces(self):
        result = clean_poem("the  wind   blows")
        assert "  " not in result

    def test_handles_multiline_poem(self):
        poem = "i walked alone\ni heard the wind"
        result = clean_poem(poem)
        lines = result.splitlines()
        assert len(lines) == 2
        for line in lines:
            assert "  " not in line

    def test_empty_string_returns_empty(self):
        result = clean_poem("")
        assert result == ""

    def test_strips_leading_trailing_whitespace_from_lines(self):
        result = clean_poem("  the river  ")
        assert not result.startswith(" ")


# ─────────────────────────────────────────────
# create_ngrams
# ─────────────────────────────────────────────

class TestCreateNgrams:

    def test_returns_a_dict(self):
        result = create_ngrams(["one two three four five six"])
        assert isinstance(result, dict)

    def test_single_line_produces_correct_key(self):
        result = create_ngrams(["one two three four five six"])
        assert ("one", "two") in result

    def test_single_line_produces_correct_ngram_value(self):
        result = create_ngrams(["one two three four five six"])
        assert ["one", "two", "three", "four"] in result[("one", "two")]

    def test_line_shorter_than_ngram_size_produces_no_entries(self):
        result = create_ngrams(["one two three"])
        assert len(result) == 0

    def test_multiple_lines_produce_separate_keys(self):
        lines = ["one two three four five six", "seven eight nine ten eleven twelve"]
        result = create_ngrams(lines)
        assert ("one", "two") in result
        assert ("seven", "eight") in result

    def test_words_are_lowercased(self):
        result = create_ngrams(["The River Flows Onward Into Night"])
        assert ("the", "river") in result

    def test_punctuation_stripped_from_keys(self):
        result = create_ngrams(["end. of. the. line. right. here."])
        for key in result:
            for word in key:
                assert "." not in word

    def test_empty_corpus_returns_empty_dict(self):
        result = create_ngrams([])
        assert result == {}

    def test_sliding_window_produces_multiple_keys(self):
        # A 7-word line with N_GRAM_SIZE=6 should produce two overlapping ngrams
        result = create_ngrams(["one two three four five six seven"])
        assert ("one", "two") in result
        assert ("two", "three") in result


# ─────────────────────────────────────────────
# create_line
# ─────────────────────────────────────────────

class TestCreateLine:

    def setup_method(self):
        # Build a small dict that mirrors what create_ngrams would produce
        self.ngram_dict = defaultdict(list)
        ngrams = [
            ["the", "river", "runs", "deep", "tonight", "burning"],
            ["river", "runs", "deep", "tonight", "burning", "bright"],
            ["deep", "tonight", "burning", "bright", "the", "stars"],
            ["tonight", "burning", "bright", "the", "stars", "fall"],
        ]
        for ngram in ngrams:
            self.ngram_dict[tuple(ngram[:2])].append(ngram)

    def test_returns_a_string(self):
        result = create_line(self.ngram_dict, "the")
        assert isinstance(result, str)

    def test_line_starts_with_seed_word(self):
        result = create_line(self.ngram_dict, "the")
        assert result.lower().startswith("the")

    def test_line_is_not_empty(self):
        result = create_line(self.ngram_dict, "river")
        assert len(result.strip()) > 0

    def test_seed_word_not_in_corpus_produces_empty_line(self):
        result = create_line(self.ngram_dict, "zzz")
        assert result == ""


# ─────────────────────────────────────────────
# prompt_seed_word
# ─────────────────────────────────────────────

class TestPromptSeedWord:

    def setup_method(self):
        self.ngram_dict = defaultdict(list)
        ngrams = [
            ["the", "river", "runs", "deep", "tonight", "burning"],
            ["river", "runs", "deep", "tonight", "burning", "bright"],
        ]
        for ngram in ngrams:
            self.ngram_dict[tuple(ngram[:2])].append(ngram)

    def test_valid_word_on_first_try(self):
        with patch("builtins.input", return_value="the"):
            result = prompt_seed_word(self.ngram_dict)
        assert result == "the"

    def test_retries_until_valid_word_found(self):
        with patch("builtins.input", side_effect=["zzz", "xyz", "river"]):
            result = prompt_seed_word(self.ngram_dict)
        assert result == "river"

    def test_returns_lowercased_word(self):
        with patch("builtins.input", return_value="THE"):
            result = prompt_seed_word(self.ngram_dict)
        assert result == "the"


# ─────────────────────────────────────────────
# save_poem
# ─────────────────────────────────────────────

class TestSavePoem:

    def test_file_is_written_with_correct_content(self):
        m = mock_open()
        with patch("builtins.input", return_value="test_poem"), \
             patch("builtins.open", m):
            save_poem("the river runs deep.")
        m().write.assert_called_once_with("the river runs deep.")

    def test_filename_uses_title(self):
        m = mock_open()
        with patch("builtins.input", return_value="my poem"), \
             patch("builtins.open", m):
            save_poem("some content")
        opened_filename = m.call_args[0][0]
        assert "my_poem" in opened_filename
        assert opened_filename.endswith(".txt")