import random
from termcolor import colored

print(colored("---------------MARKOV CHAIN POETRY GENERATOR---------------",
              "blue",
              "on_grey",
              attrs=["bold"], force_color=True))

def main(poem=""):
    quadruplets = []

    with open("poetry_lines.txt", encoding="utf-8") as f:
        poetry_lines = f.readlines()

    for line in poetry_lines:
        # split a corpus sentence into individual words
        words = [w.lower()
                 .replace(".", "")
                            for w in line.split()]

        # stagger the start of each quad throughout the sentence
        for i in range(len(words) - 3):
            quad = []
            quad.append(words[i])
            quad.append(words[i + 1])
            quad.append(words[i + 2])
            quad.append(words[i + 3])
            quadruplets.append(quad)

    # always ask for the first word of each line
    word = input("What should the first word of this line be? ").lower()
    print()

    # reset input if no quad starts with their word
    while not any(quad[0] == word for quad in quadruplets):
        word = input("Word not found in corpus. Try again: ").lower()

    this_line = ""

    for _ in range(5):
        try:
            # append next quad to the sentence
            quads = [quad for quad in quadruplets if quad[0].lower() == word.lower()]
            chosen_quad = random.choice(quads)
            if _ == 0:
                this_line += " ".join(chosen_quad)
            else:
                # don't add first word if it's not the first quad so the word doesn't repeat
                this_line += " ".join(chosen_quad[1:])
            word = chosen_quad[3]
            this_line += " "
        except IndexError:
            break

    finalized_line = this_line.capitalize().strip()
    print(finalized_line + "\n")

    finalized_poem = (poem.strip()
                      .replace(" i ", " I ")
                      .replace("i'", "I'")
                      .replace("  ", " ")
                      .replace(",", "")
                      + ".")

    choice = input("""Do you want to:
    (1) Append to your poem?
    (2) Retry this line?
    (3) Print final poem and quit?
    (4) Save to file and quit?
    (5) Quit? """).strip()

    enjoy = "***********ENJOY YOUR NEW POEM!***********"

    match choice:
        case "1":
            poem += "\n" + finalized_line
            print(poem + '\n')
            main(poem)
        case "2":
            print(poem + "\n")
            main(poem)
        case "3":
            poem += "\n" + finalized_line
            print("\n" + finalized_poem + "\n")
            print(enjoy)
        case "4":
            title = input("\nWhat do you want to name this poem? ").strip()
            filename = title + '.txt'
            with open(filename, 'w') as file:
                poem += "\n" + finalized_line
                print(f'\n"{title.capitalize()}"')
                print("\n" + finalized_poem)
                file.write(finalized_poem)
                print(f"\nfile saved as {filename}\n")
                print(enjoy)

        case _:
            poem += "\n" + finalized_line
            print("\n" + finalized_poem + "\n")
            print(enjoy)

if __name__ == '__main__':
    main()