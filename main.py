import random
from termcolor import colored
import re
from datetime import datetime

"""
Since the corpus is relatively small and the goal is poetic surprise rather than strict linguistic coherence, 
one-word transitions produce more varied and interesting output while avoiding frequent dead ends.
"""

QUADRUPLET_SIZE = 4
WORDS_PER_LINE = 5  # Number of quads to chain
ENJOY = "***********ENJOY YOUR NEW POEM!***********"


def print_header():
    print(
        colored(
            "---------------MARKOV CHAIN POETRY GENERATOR---------------",
            "blue",
            "on_grey",
            attrs=["bold"],
            force_color=True,
        )
    )


def load_file():
    with open("poetry_lines.txt", encoding="utf-8") as f:
        poetry_lines = f.readlines()

        all_words = [
            word.lower().strip(".,!?;:\"'()") for line in poetry_lines for word in line.split()
        ]
        all_words = [word for word in all_words if word]
        total_words = len(all_words)
        unique_words = len(set(all_words))

        print("Corpus loaded:")
        print(f"- {len(poetry_lines)} lines")
        print(f"- {total_words} total words")
        print(f"- {unique_words} unique words")
        print(f"- {unique_words / total_words:.1%} unique-word ratio\n")

        return poetry_lines


def clean_poem(poem: str) -> str:
    lines = poem.strip().splitlines()
    cleaned_lines = []

    for line in lines:
        line = line.strip()
        line = re.sub(r"\bi\b", "I", line)
        line = re.sub(r" {2,}", " ", line)
        cleaned_lines.append(line)

    poem = "\n".join(cleaned_lines)

    if poem and poem[-1] not in ".!?":
        poem += "."

    return poem


def create_quads(poetry_lines: list[str]) -> list[list[str]]:
    """Create the quadruplet word sections."""
    quadruplets = []
    for line in poetry_lines:

        # Normalize each word to lowercase and strip punctuation
        words = [w.lower().replace(".", "") for w in line.split()]

        # Slide a 4-word window across the line to generate all possible quadruplets
        quadruplets.extend(
            words[i : i + QUADRUPLET_SIZE] for i in range(len(words) - QUADRUPLET_SIZE + 1)
        )

    return quadruplets


def prompt_seed_word(quadruplets: list[list[str]]) -> str:
    word = input("What should the first word of this line be? ").lower().strip()
    print()

    # Reject any seed word that doesn't appear at the start of a quadruplet
    while not any(quad[0] == word for quad in quadruplets):
        word = input("Word not found in corpus. Try again: ").lower().strip()

    return word


def create_line(quadruplets: list[list[str]], word: str) -> str:
    """Build a single poem line by chaining together quadruplets via Markov-style traversal."""
    # Prompt the user for a seed word to begin the generated line
    new_line = ""
    for index in range(WORDS_PER_LINE):
        # Find all quadruplets that begin with the current word
        quads = [quad for quad in quadruplets if quad[0] == word]
        if quads:
            chosen_quad = random.choice(quads)
            if index == 0:
                # First quad: include all four words
                new_line += " ".join(chosen_quad)
            else:
                # Subsequent quads: skip the first word to avoid repetition at the join
                new_line += " ".join(chosen_quad[1:])
            # The last word of the chosen quad becomes the seed for the next iteration
            word = chosen_quad[-1]
            new_line += " "
    return new_line.strip()


def save_poem(final_poem: str):
    # Prompt for a title, save the poem to a .txt file, and confirm to the user
    title = input("\nWhat do you want to name this poem? ").strip()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{title.strip().replace(' ', '_').lower()}_{timestamp}.txt"
    with open(filename, "w") as file:
        file.write(final_poem)
    print(f"Saved as '{filename}'")


def main():
    print_header()

    # Load the poetry corpus used to build the Markov chain
    try:
        poetry_lines = load_file()
    except FileNotFoundError:
        print("Error: poetry_lines.txt was not found.")
        return

    poem = ""
    quadruplets = create_quads(poetry_lines)
    

    while True:
        word = prompt_seed_word(quadruplets)
        new_line = create_line(quadruplets, word)

        finalized_line = new_line.capitalize()
        print(f"{finalized_line}\n")

        while True:
            choice = input("""Do you want to:
            (1) Append to your poem and continue?
            (2) Retry this line?
            (3) Print final poem and quit?
            (4) Save and quit? """).strip()

            match choice:
                case "1":
                    # Add the line to the poem and generate the next line
                    poem += "\n" + finalized_line
                    print(f"{poem}\n")
                    break
                case "2":
                    # Discard line and try again within the existing poem
                    print(f"{poem}\n")
                    break
                case "3":
                    # Finalize, display, exit
                    poem += "\n" + finalized_line
                    final_poem = clean_poem(poem)
                    print(f"\n{final_poem}\n{ENJOY}")
                    return
                case "4":
                    # Finalize, clean, save, display, exit
                    poem += "\n" + finalized_line
                    final_poem = clean_poem(poem)
                    save_poem(final_poem)
                    print(f"\n{final_poem}\n{ENJOY}")
                    return

                case _:
                    print("Please enter a valid choice.")


if __name__ == "__main__":
    main()
