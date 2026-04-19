import pytest
from unittest.mock import patch, mock_open
from main import clean_poem, create_quads, create_line, save_poem, prompt_seed_word


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
        # clean_poem guards with `if poem:` so empty input stays empty
        result = clean_poem("")
        assert result == ""

    def test_strips_leading_trailing_whitespace_from_lines(self):
        result = clean_poem("  the river  ")
        assert not result.startswith(" ")


# ─────────────────────────────────────────────
# create_quads
# ─────────────────────────────────────────────

class TestCreateQuads:

    def test_single_line_four_words_produces_one_quad(self):
        result = create_quads(["one two three four"])
        assert result == [["one", "two", "three", "four"]]

    def test_single_line_five_words_produces_two_quads(self):
        result = create_quads(["one two three four five"])
        assert result == [
            ["one", "two", "three", "four"],
            ["two", "three", "four", "five"],
        ]

    def test_line_shorter_than_four_words_produces_no_quads(self):
        result = create_quads(["one two three"])
        assert result == []

    def test_multiple_lines_combined(self):
        lines = ["one two three four", "five six seven eight"]
        result = create_quads(lines)
        assert ["one", "two", "three", "four"] in result
        assert ["five", "six", "seven", "eight"] in result

    def test_words_are_lowercased(self):
        result = create_quads(["The River Flows Onward"])
        assert result == [["the", "river", "flows", "onward"]]

    def test_periods_stripped_from_words(self):
        result = create_quads(["end. of. the. line."])
        for quad in result:
            for word in quad:
                assert "." not in word

    def test_empty_corpus_returns_empty_list(self):
        result = create_quads([])
        assert result == []


# ─────────────────────────────────────────────
# create_line
# ─────────────────────────────────────────────

class TestCreateLine:

    def setup_method(self):
        self.quads = [
            ["the", "river", "runs", "deep"],
            ["river", "runs", "deep", "tonight"],
            ["deep", "tonight", "the", "stars"],
            ["tonight", "the", "stars", "burn"],
        ]

    def test_returns_a_string(self):
        result = create_line(self.quads, "the")
        assert isinstance(result, str)

    def test_line_starts_with_seed_word(self):
        result = create_line(self.quads, "the")
        assert result.lower().startswith("the")

    def test_line_is_not_empty(self):
        result = create_line(self.quads, "river")
        assert len(result.strip()) > 0

    def test_seed_word_not_in_corpus_produces_empty_line(self):
        result = create_line(self.quads, "zzz")
        assert result == ""


# ─────────────────────────────────────────────
# prompt_seed_word
# ─────────────────────────────────────────────

class TestPromptSeedWord:

    def setup_method(self):
        self.quads = [
            ["the", "river", "runs", "deep"],
            ["river", "runs", "deep", "tonight"],
        ]

    def test_valid_word_on_first_try(self):
        with patch("builtins.input", return_value="the"):
            result = prompt_seed_word(self.quads)
        assert result == "the"

    def test_retries_until_valid_word_found(self):
        with patch("builtins.input", side_effect=["zzz", "xyz", "river"]):
            result = prompt_seed_word(self.quads)
        assert result == "river"

    def test_returns_lowercased_word(self):
        with patch("builtins.input", return_value="THE"):
            result = prompt_seed_word(self.quads)
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