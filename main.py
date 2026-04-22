import random
import re
from datetime import datetime
from collections import defaultdict
from tqdm import tqdm

# Controls how many words form the lookup key in the transition table.
# Smaller keys (2) mean more matches per lookup — wilder, more surprising output.
# Larger keys (3+) produce more coherent phrases but start to echo source lines.
KEY_SIZE = 2

# Shorter n-grams produce wilder output; longer ones risk more dead ends and start to reproduce source lines.
N_GRAM_SIZE = 4

# 6 chained 4-grams with 2-word overlaps.
GRAMS_PER_LINE = 6

ENJOY = "***********ENJOY YOUR NEW POEM!***********"


def load_file() -> list[str]:
    """Load the corpus from poetry_lines.txt and print a brief summary."""
    with open("poetry_lines.txt", encoding="utf-8") as f:
        poetry_lines = f.readlines()

    # Flatten to a word list just for the stats printout.
    # This is separate from the model-building pass in create_ngrams.
    all_words = [
        word.lower().strip('.,!?;:"\'()"') for line in poetry_lines for word in line.split()
    ]
    all_words = [word for word in all_words if word]

    total_words = len(all_words)
    unique_words = len(set(all_words))

    print("Corpus loaded:")
    print(f"- {len(poetry_lines):,} lines")
    print(f"- {total_words:,} total words")
    print(f"- {unique_words:,} unique words")
    print(f"- {unique_words / total_words:.1%} unique-word ratio\n")

    return poetry_lines


def create_ngrams(poetry_lines: list[str]) -> dict[tuple, list]:
    """Slide an n-gram window across each line to build the Markov transition table.

    Each word chunk is stored under a tuple key representing
    This allows O(1) lookup during line generation.
    Lines are processed individually so n-grams never cross line boundaries.

    Returns:
        A defaultdict mapping (word1, word2, word3) tuples to lists of
        matching n-grams.
    """
    print("Creating ngrams, please wait...")
    ngram_dict = defaultdict(list)

    for line in tqdm(poetry_lines, desc="Building model"):
        # Punctuation is stripped minimally — only enough to avoid broken keys.
        # Keeping some punctuation gives generated lines organic texture.
        words = [w.lower().strip(".,!?;:\"'()\u201c\u201d\u2018\u2019") for w in line.split()]

        for i in range(len(words) - N_GRAM_SIZE + 1):
            ngram = words[i : i + N_GRAM_SIZE]
            # Key is the first 3 words; value is the full 6-word n-gram.
            ngram_dict[tuple(ngram[:KEY_SIZE])].append(ngram)

    return ngram_dict


def prompt_seed_word(ngram_dict: dict[tuple, list]) -> str:
    """Prompt the user for a seed word and validate it against the model.

    Only words that appear as the first element of an n-gram key are accepted.
    This guarantees at least one valid n-gram exists to start the chain —
    a word that only appears mid-line has no key to chain from.
    """
    word = input("What should the first word of this line be? ").lower().strip()
    print()

    # Iterate over keys (3-word tuples) and check the first element of each.
    while not any(key[0] == word for key in ngram_dict):
        word = input("Word not found in corpus. Try again: ").lower().strip()

    return word


def create_line(ngram_dict: dict[tuple, list], word: str) -> str:
    """Chain n-grams together, overlaps to build a single poem line.

    Starting from the seed word, a random key beginning with that word
    is chosen. Each step looks up the current key in the model, picks a random
    matching n-gram, appends the new words (skipping the ones already written),
    then slides the key forward.
    """
    new_line = ""

    # Collect all keys whose first word matches the seed, then pick one at random.
    matching_keys = [k for k in ngram_dict if k[0] == word]

    # If no matching keys, return empty string
    if not matching_keys:
        return ""

    word_triple = random.choice(matching_keys)

    for index in range(GRAMS_PER_LINE):
        grams = ngram_dict[word_triple]
        if not grams:
            # Dead end: no n-gram exists for the current key.
            # A shorter line is better than a broken or padded one.
            break

        chosen_gram = random.choice(grams)

        if index == 0:
            # First iteration: write the full 6-word n-gram.
            new_line += " ".join(chosen_gram)
        else:
            # Subsequent iterations: skip the first 3 words since they were
            # already written as the tail of the previous n-gram.
            new_line += " ".join(chosen_gram[KEY_SIZE:])

        # Slide the key forward to the last 3 words of the chosen n-gram.
        word_triple = tuple(chosen_gram[-KEY_SIZE:])
        new_line += " "

    return new_line.strip()


def clean_poem(poem: str) -> str:
    """Light post-processing on the assembled poem before display or save."""
    lines = poem.strip().splitlines()
    cleaned_lines = []

    for line in lines:
        line = line.strip()
        line = re.sub(r"\bi\b", "I", line)  # fix lowercase 'i' without touching 'in', 'it', etc.
        line = re.sub(r" {2,}", " ", line)  # collapse extra spaces left by n-gram joins
        cleaned_lines.append(line)

    poem = "\n".join(cleaned_lines)

    # Ensure the poem ends with terminal punctuation so it feels complete.
    if poem and poem[-1] not in ".!?":
        poem += "."

    return poem


def save_poem(final_poem: str) -> str:
    """Prompt for a title and write the finished poem to a timestamped .txt file."""
    title = input("\nWhat do you want to name this poem? ").strip()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{title.strip().replace(' ', '_').lower()}_{timestamp}.txt"

    with open(filename, "w") as file:
        file.write(final_poem)

    return filename


def main():
    print("---------------MARKOV CHAIN POETRY GENERATOR---------------\nLoading corpus...")

    try:
        poetry_lines = load_file()
    except FileNotFoundError:
        print("Error: poetry_lines.txt was not found.")
        return

    ngram_dict = create_ngrams(poetry_lines)

    while True:
        word = prompt_seed_word(ngram_dict)
        new_line = create_line(ngram_dict, word)
        finalized_line = new_line.capitalize()
        print(f"{finalized_line}\n")

        poem = ""
        while True:
            choice = input("""Do you want to:
            (1) Append to your poem and continue?
            (2) Retry this line?
            (3) Print final poem and quit?
            (4) Save and quit? """).strip()
            match choice:
                case "1":
                    poem += "\n" + finalized_line
                    print(f"{poem}\n")
                    break
                case "2":
                    print(f"{poem}\n")
                    break
                case "3":
                    poem += "\n" + finalized_line
                    final_poem = clean_poem(poem)
                    print(f"\n{final_poem}\n{ENJOY}")
                    return
                case "4":
                    poem += "\n" + finalized_line
                    final_poem = clean_poem(poem)
                    filename = save_poem(final_poem)
                    print(f"Saved as '{filename}'")
                    print(f"\n{final_poem}\n{ENJOY}")
                    return
                case _:
                    print("Please enter a valid choice.")


if __name__ == "__main__":
    main()

"""
Under Development

- Model caching:
Serialize the transition table to disk with pickle after the first build, 
reload it on subsequent runs instead of rebuilding from scratch. 
Cache invalidation based on the corpus file's modification timestamp so stale caches are detected automatically.

- Configurable corpus path:
accept the corpus filename as a command-line argument via argparse rather than hardcoding poetry_lines.txt.

- Multiple seed words:
allow the user to specify two or three seed words to give more control over where the line begins, 
making use of the full key tuple rather than just the first word.

- Streamlit GUI:
a browser-based interface for the generator, making it accessible without the command line and allowing the poem to be displayed and edited in real time.

- Adjustable constants at runtime:
expose N_GRAM_SIZE, KEY_SIZE, and GRAMS_PER_LINE as interactive prompts or flags so the output character can be tuned per session without editing the source file.
"""
