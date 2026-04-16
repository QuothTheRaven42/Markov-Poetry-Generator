import random
from termcolor import colored

print(
    colored(
        "---------------MARKOV CHAIN POETRY GENERATOR---------------",
        "blue",
        "on_grey",
        attrs=["bold"],
        force_color=True,
    )
)


def clean_poem(poem: str) -> str:
    # Trim whitespace, fix lowercase "i", collapse double spaces, and close with a period
    return poem.strip().replace(" i ", " I ").replace("i'", "I'").replace("  ", " ") + "."


def create_quads(poetry_lines: list) -> list:
    """Create the quadruplet word sections."""
    quadruplets = []
    for line in poetry_lines:

        # Normalize each word to lowercase and strip punctuation
        words = [w.lower().replace(".", "") for w in line.split()]

        # Slide a 4-word window across the line to generate all possible quadruplets
        quadruplets.extend(words[i : i + 4] for i in range(len(words) - 3))

    return quadruplets


def create_line(quadruplets: list, word: str) -> str:
    """Build a single poem line by chaining together quadruplets via Markov-style traversal."""
    new_line = ""
    for index in range(5):
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
            word = chosen_quad[3]
            new_line += " "
    return new_line.strip()


def save_poem(final_poem: str, enjoy: str):
    # Prompt for a title, save the poem to a .txt file, and confirm to the user
    title = input("\nWhat do you want to name this poem? ").strip()
    filename = title + ".txt"
    with open(filename, "w") as file:
        print(f'\n"{title.title()}"\n{final_poem}')
        file.write(final_poem)
        print(f"\nfile saved as {filename}\n\n{enjoy}")


def main(poem=""):
    # Load the poetry corpus used to build the Markov chain
    with open("poetry_lines.txt", encoding="utf-8") as f:
        poetry_lines = f.readlines()

    quadruplets = create_quads(poetry_lines)

    # Prompt the user for a seed word to begin the generated line
    word = input("What should the first word of this line be? ").lower().strip()
    print()

    # Reject any seed word that doesn't appear at the start of a quadruplet
    while not any(quad[0] == word for quad in quadruplets):
        word = input("Word not found in corpus. Try again: ").lower().strip()

    new_line = create_line(quadruplets, word)

    finalized_line = new_line.capitalize()
    print(f"{finalized_line}\n")

    enjoy = "***********ENJOY YOUR NEW POEM!***********"
    choice = "_"
    while choice not in ["1", "2", "3", "4"]:
        choice = input("""Do you want to:
        (1) Append to your poem?
        (2) Retry this line?
        (3) Print final poem and quit?
        (4) Print and quit? """).strip()

        match choice:
            case "1":
                # Add the new line to the poem and recurse to generate the next line
                poem += "\n" + finalized_line
                print(f"{poem}\n")
                main(poem)
            case "2":
                # Discard this line and recurse to try again with the existing poem
                print(f"{poem}\n")
                main(poem)
            case "3":
                # Finalize, clean, and display the complete poem without saving
                poem += "\n" + finalized_line
                final_poem = clean_poem(poem)
                print(f"\n{final_poem}\n{enjoy}")
            case "4":
                # Finalize and display, then exit
                poem += "\n" + finalized_line
                final_poem = clean_poem(poem)
                print(f"\n{final_poem}\n{enjoy}")

            case _:
                print("Please enter a valid choice.")


if __name__ == "__main__":
    main()
