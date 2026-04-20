import re
import tkinter as tk
from tkinter import filedialog, messagebox
from tqdm import tqdm
import os

ROMAN_NUMERAL_TOKEN = re.compile(
    r"\b(m{0,4}(cm|cd|d?c{0,3})(xc|xl|l?x{0,3})(ix|iv|v?i{0,3}))\b\.?",
    re.IGNORECASE,
)


def clean_token(token: str) -> str:
    return token.strip(".,!?;:\"'()").lower()


def has_digit(line: str) -> bool:
    return any(char.isdigit() for char in line)


def has_standalone_roman(line: str) -> bool:
    """Match lines where a token is purely a Roman numeral (optionally with a period).
    Avoids nuking real words that happen to share letters like 'live' or 'mix'."""
    for token in line.split():
        token_clean = clean_token(token)
        if token_clean and ROMAN_NUMERAL_TOKEN.fullmatch(token_clean):
            return True
    return False


def remove_long_words(line: str) -> bool:
    for token in line.split():
        token_clean = clean_token(token)
        if len(token_clean) > 19:
            return True
    return False


def no_vowels(line: str) -> bool:
    for token in line.split():
        token_clean = clean_token(token)
        if len(token_clean) > 2 and not any(char in "aeiou" for char in token_clean):
            return True
    return False


def should_remove(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if has_digit(stripped):
        return True
    if has_standalone_roman(stripped):
        return True
    if remove_long_words(stripped):
        return True
    if no_vowels(stripped):
        return True
    return False

def run_cleaning(filepath: str):
    print("\nReading file...")
    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()

    total = len(lines)
    print(f"Loaded {total:,} lines.\n")

    kept = []
    removed = 0

    for line in tqdm(lines, desc="Cleaning", unit="line"):
        if should_remove(line):
            removed += 1
        else:
            kept.append(line)

    print(f"\nRemoved: {removed:,} lines ({removed / total:.1%})")
    print(f"Kept:    {len(kept):,} lines")

    print("\nOverwriting file...")
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(kept)

    print("Done.")


def browse_file(entry: tk.Entry):
    path = filedialog.askopenfilename(
        title="Select your corpus .txt file",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
    )
    if path:
        entry.delete(0, tk.END)
        entry.insert(0, path)


def on_run(entry: tk.Entry):
    filepath = entry.get().strip()
    if not filepath:
        messagebox.showerror("Missing input", "Please select a .txt file first.")
        return


    if not os.path.isfile(filepath):
        messagebox.showerror("File not found", f"Could not find:\n{filepath}")
        return
    run_cleaning(filepath)
    messagebox.showinfo("Complete", "Cleaning finished. Check the terminal for details.")


def main():
    root = tk.Tk()
    root.title("Corpus Cleaner")
    root.resizable(False, False)

    pad = {"padx": 10, "pady": 6}

    tk.Label(root, text="Corpus .txt file:").grid(row=0, column=0, sticky="w", **pad)
    file_entry = tk.Entry(root, width=55)
    file_entry.grid(row=0, column=1, **pad)
    tk.Button(root, text="Browse…", command=lambda: browse_file(file_entry)).grid(
        row=0, column=2, **pad
    )

    tk.Button(
        root,
        text="Run Cleaning",
        command=lambda: on_run(file_entry),
        bg="#4a7fc1",
        fg="white",
        padx=12,
        pady=4,
    ).grid(row=1, column=1, pady=12)

    root.mainloop()


if __name__ == "__main__":
    main()
