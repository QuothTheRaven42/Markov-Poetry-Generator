# Markov Chain Poetry Generator

A command-line tool that generates original poetry lines using a Markov chain algorithm trained on a custom corpus of poetry. The generator builds word sequences (quadruplets) from the corpus and chains them together based on your chosen starting word, producing unpredictable but corpus-flavored lines.

## Features

- Generates lines by chaining 4-word sequences drawn from a poetry corpus
- Interactive prompt lets you choose the first word of each line
- Build a multi-line poem incrementally, one line at a time
- Print your finished poem to the terminal or save it as a `.txt` file
- Colored terminal header via `termcolor`

## Requirements

- Python 3.10+
- [termcolor](https://pypi.org/project/termcolor/)

Install the dependency with:

```
pip install termcolor
```

## Setup

The generator reads from a file called `poetry_lines.txt` in the same directory as the script. Each line in the file should be a line of poetry from your corpus. The broader and more varied the corpus, the more interesting the output.

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
| 5 | Quit |

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
    (1) Append to your poem?
    (2) Retry this line?
    ...
```
