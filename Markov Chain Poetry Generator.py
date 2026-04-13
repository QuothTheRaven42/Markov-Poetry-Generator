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
    return (poem.strip()
            .replace(" i ", " I ")
            .replace("i'", "I'")
            .replace("  ", " ")
            + ".")


def main(poem=""):
    with open("poetry_lines.txt", encoding="utf-8") as f:
        poetry_lines = f.readlines()

    quadruplets = []
    for line in poetry_lines:
        # split a corpus sentence into individual words
        words = [w.lower().replace(".", "") for w in line.split()]

        # stagger the start of each quad throughout the sentence
        quadruplets.extend(words[i : i + 4] for i in range(len(words) - 3))

    # always ask for the first word of each line
    word = input("What should the first word of this line be? ").lower().strip()
    print()

    # reset input if no quad starts with their word
    while not any(quad[0] == word for quad in quadruplets):
        word = input("Word not found in corpus. Try again: ").lower().strip()

    this_line = ""

    for index in range(5):
        # append next quads to the sentence
        quads = [quad for quad in quadruplets if quad[0] == word]
        if quads:
            chosen_quad = random.choice(quads)
            if index == 0:
                this_line += " ".join(chosen_quad)
            else:
                # don't add first word if it's not the first quad so the word doesn't repeat
                this_line += " ".join(chosen_quad[1:])
            word = chosen_quad[3]
            this_line += " "

    finalized_line = this_line.capitalize().strip()
    print(finalized_line + "\n")

    enjoy = "***********ENJOY YOUR NEW POEM!***********"
    choice = "_"
    while choice not in ["1", "2", "3", "4", "5"]:
        choice = input("""Do you want to:
        (1) Append to your poem?
        (2) Retry this line?
        (3) Print final poem and quit?
        (4) Save to file and quit?
        (5) Quit? """).strip()

        match choice:
            case "1":
                poem += "\n" + finalized_line
                print(poem + "\n")
                main(poem)
            case "2":
                print(poem + "\n")
                main(poem)
            case "3":
                poem += "\n" + finalized_line
                final_poem = clean_poem(poem)
                print(f"\n{final_poem}\n{enjoy}")
            case "4":
                title = input("\nWhat do you want to name this poem? ").strip()
                filename = title + ".txt"
                with open(filename, "w") as file:
                    poem += "\n" + finalized_line
                    final_poem = clean_poem(poem)
                    print(f'\n"{title.title()}"\n{final_poem}')
                    file.write(final_poem)
                    print(f"\nfile saved as {filename}\n\n{enjoy}")
            case "5":
                poem += "\n" + finalized_line
                final_poem = clean_poem(poem)
                print(f"\n{final_poem}\n{enjoy}")

            case _:
                print("Please enter a valid choice.")


if __name__ == "__main__":
    main()


"""
Planned Improvement:
The recursive main(poem) calls are the most significant issue:
It also re-reads and rebuilds quadruplets from the file on every call, which is unnecessary work. 
A while loop would handle the poem-building more cleanly.
"""
