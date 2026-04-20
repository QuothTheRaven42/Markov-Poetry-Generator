# Markov Chain Poetry Generator
A command-line poetry generator that creates original lines from a custom corpus of poetry using a Markov-style chaining system. The program builds overlapping n-gram sequences from the corpus and links them together from a user-chosen starting word, producing language that is often surprising, dreamlike, and flavored by the source material.

## Features
- Generates poetry from a text corpus of lines
- Builds an n-gram transition model with configurable chunk size and key size
- O(1) lookup via a dict-based model — handles large corpora efficiently
- Lets the user choose the starting word for each generated line
- Supports building a poem incrementally, one line at a time
- Can print the final poem to the terminal or save it as a `.txt` file

## Design & Technical Choices
Standard n-gram Markov chains often require much larger text corpora to avoid dead-ending, which makes them harder to use with small, specialized poetry collections.

To solve this and encourage more surreal, poetic leaps, this generator uses a custom overlapping strategy:

1. It breaks the source text into overlapping n-word chunks controlled by `N_GRAM_SIZE`.
2. Chunks are indexed by a shorter `KEY_SIZE`-word tuple, so each lookup step finds all chunks that continue naturally from the current position.
3. It transitions between chunks by overlapping the tail of one chunk with the head of the next, producing lines that flow while still making unexpected associative jumps.

This hybrid approach preserves brief moments of original phrasing while creating abrupt, surprising leaps between them — better suited to poetry than to coherent prose.

The transition table is stored as a `defaultdict` keyed by word tuples, so each generation step is an O(1) dict lookup rather than a scan of the full model. This makes the generator practical even on very large corpora.

The two constants at the top of the script control the character of the output:
- **`N_GRAM_SIZE`** — the length of each chunk. Larger chunks produce more verbatim source phrasing.
- **`KEY_SIZE`** — the number of words used as a lookup key. Smaller keys produce wilder, more unpredictable output; larger keys produce more coherent but less surprising lines.

## Requirements
- Python 3.10+
- [tqdm](https://pypi.org/project/tqdm/)

Install the dependency with:
```
pip install tqdm
```

## Setup
The generator reads from a file called `poetry_lines.txt` in the same directory as the script.

Each line in the file should be a line of poetry or prose from your corpus. The broader and more varied the corpus, the more interesting the output.

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
- Building the model on large corpora takes a moment — a progress bar is shown during this step

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
The route in her that was also its own answer I'd been rehearsing for years and
Whenever she felt herself and updated them needing to stop looking for it couldn't quite reach
So precisely that I realized I'd been on before in the room had been composing for
Quite believing in itself that had given it back as old enough now in the process.
```

---

## Under Development
Planned improvements and ideas for future versions:

- **Model caching** — serialize the transition table to disk with `pickle` after the first build, and reload it on subsequent runs instead of rebuilding from scratch. Cache invalidation based on the corpus file's modification timestamp so stale caches are detected automatically.
- **Configurable corpus path** — accept the corpus filename as a command-line argument via `argparse` rather than hardcoding `poetry_lines.txt`.
- **Multiple seed words** — allow the user to specify two or three seed words to give more control over where the line begins, making use of the full key tuple rather than just the first word.
- **Line count control** — let the user specify how many lines to generate automatically before reviewing, rather than confirming after each one.
- **Streamlit GUI** — a browser-based interface for the generator, making it accessible without the command line and allowing the poem to be displayed and edited in real time.
- **Adjustable constants at runtime** — expose `N_GRAM_SIZE`, `KEY_SIZE`, and `GRAMS_PER_LINE` as interactive prompts or flags so the output character can be tuned per session without editing the source file.
