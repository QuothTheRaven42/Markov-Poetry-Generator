# Markov Chain Poetry Generator

A command-line poetry generator that creates original lines from a custom corpus of poetry using a loose Markov-style chaining system. The program builds overlapping 4-word sequences from the corpus and links them together from a user-chosen starting word, producing language that is often surprising, dreamlike, and flavored by the source material.

## Features

- Generates poetry from a text corpus of prose lines
- Builds overlapping 4-word sequences from the corpus
- Lets the user choose the starting word for each generated line
- Supports building a poem incrementally, one line at a time
- Can print the final poem to the terminal or save it as a `.txt` file

## Design & Technical Choices

Standard n-gram Markov chains often require much larger text corpora to avoid dead-ending, which makes them harder to use with small, specialized poetry collections.

To solve this and encourage more surreal, poetic leaps, this generator uses a custom overlapping strategy:
1. It breaks the source text into overlapping 4-word chunks (quadruplets).
2. It transitions between chunks by matching the **last word** of the current chunk to the **first word** of the next available chunk. 

This hybrid approach preserves brief moments of original phrasing (the 4-word chunks) while creating abrupt, surprising associative jumps between them—perfect for generating poetry rather than strict, coherent prose.


## Requirements

- Python 3.10+
- [termcolor](https://pypi.org/project/termcolor/)

Install the dependency with:

```
pip install termcolor
```

## Setup

The generator reads from a file called `poetry_lines.txt` in the same directory as the script. 

Each line in the file should be a line of poetry from your corpus. The broader and more varied the corpus, the more interesting the output.

## Usage

```
python main.py
```

You will be prompted to enter the first word of your line. If the word isn't found in the corpus, you'll be asked to try again. After each line is generated you can:

| Option | Action |
|--------|--------|
| 1 | Append the line to your poem and generate another |
| 2 | Retry the current line |
| 3 | Print the completed poem and quit |
| 4 | Save the completed poem to a `.txt` file and quit |

## Notes

- Input is case-insensitive
- The first letter of each line is automatically capitalized
- Lowercase `i` is corrected to `I` in the final poem
- Poems are saved to the directory where the script is run

## Example Output

```
What should the first word of this line be? the

The particular joy for years hoping to be

Do you want to:
    (1) Append to your poem and continue?
    (2) Retry this line?
    ...
```

### Example poem

```
The particular joy for years hoping to be
A darkened window opening into rain
The river knew the shape of every silence
```
