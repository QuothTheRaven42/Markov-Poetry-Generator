import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox

import nltk
from nltk.tokenize import sent_tokenize
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from tqdm import tqdm

# Download punkt tokenizer data on first run (silent after that)
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)

MIN_WORDS = 4


def extract_sentences_from_epub(epub_path: str) -> list[str]:
    """Extract and tokenize sentences from a single epub file."""
    sentences = []
    try:
        book = epub.read_epub(epub_path, options={"ignore_ncx": True})
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            soup = BeautifulSoup(item.get_content(), "html.parser")
            text = soup.get_text(separator=" ")
            text = re.sub(r"\s+", " ", text).strip()
            if not text:
                continue
            for sentence in sent_tokenize(text):
                sentence = sentence.strip()
                if len(sentence.split()) >= MIN_WORDS:
                    sentences.append(sentence)
    except Exception as e:
        print(f"\nSkipped {os.path.basename(epub_path)}: {e}")
    return sentences


def run_extraction(txt_path: str, epub_folder: str):
    """Load existing sentences, scrape epubs, append new ones."""

    # Load existing lines to avoid duplicates
    existing: set[str] = set()
    if os.path.exists(txt_path):
        with open(txt_path, encoding="utf-8") as f:
            existing = {line.strip() for line in f if line.strip()}
    print(f"Existing sentences in file: {len(existing)}")

    epub_files = [f for f in os.listdir(epub_folder) if f.lower().endswith(".epub")]

    if not epub_files:
        print("No .epub files found in the selected folder.")
        return

    print(f"Found {len(epub_files)} epub(s) to process.\n")

    new_sentences: list[str] = []
    for epub_file in tqdm(epub_files, desc="Processing EPUBs", unit="book"):
        epub_path = os.path.join(epub_folder, epub_file)
        for sentence in extract_sentences_from_epub(epub_path):
            if sentence not in existing:
                new_sentences.append(sentence)
                existing.add(sentence)

    with open(txt_path, "a", encoding="utf-8") as f:
        for sentence in new_sentences:
            f.write(sentence + "\n")

    print(f"\nDone. {len(new_sentences)} new sentences appended to {os.path.basename(txt_path)}.")


# ── GUI ────────────────────────────────────────────────────────────────────────


def browse_file(entry: tk.Entry):
    path = filedialog.askopenfilename(
        title="Select your poetry .txt file",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
    )
    if path:
        entry.delete(0, tk.END)
        entry.insert(0, path)


def browse_folder(entry: tk.Entry):
    path = filedialog.askdirectory(title="Select folder containing .epub files")
    if path:
        entry.delete(0, tk.END)
        entry.insert(0, path)


def on_run(txt_entry: tk.Entry, folder_entry: tk.Entry):
    txt_path = txt_entry.get().strip()
    folder_path = folder_entry.get().strip()

    if not txt_path or not folder_path:
        messagebox.showerror("Missing input", "Please select both a .txt file and an epub folder.")
        return
    if not os.path.isfile(txt_path):
        messagebox.showerror("File not found", f"Could not find:\n{txt_path}")
        return
    if not os.path.isdir(folder_path):
        messagebox.showerror("Folder not found", f"Could not find:\n{folder_path}")
        return

    print(f"\nAppending to:   {txt_path}")
    print(f"EPUB folder:    {folder_path}\n")
    run_extraction(txt_path, folder_path)


def main():
    root = tk.Tk()
    root.title("EPUB Sentence Extractor")
    root.resizable(False, False)

    pad = {"padx": 10, "pady": 6}

    tk.Label(root, text="Poetry .txt file:").grid(row=0, column=0, sticky="w", **pad)
    txt_entry = tk.Entry(root, width=55)
    txt_entry.grid(row=0, column=1, **pad)
    tk.Button(root, text="Browse…", command=lambda: browse_file(txt_entry)).grid(
        row=0, column=2, **pad
    )

    tk.Label(root, text="EPUB folder:").grid(row=1, column=0, sticky="w", **pad)
    folder_entry = tk.Entry(root, width=55)
    folder_entry.grid(row=1, column=1, **pad)
    tk.Button(root, text="Browse…", command=lambda: browse_folder(folder_entry)).grid(
        row=1, column=2, **pad
    )

    tk.Button(
        root,
        text="Run Extraction",
        command=lambda: on_run(txt_entry, folder_entry),
        bg="#4a7fc1",
        fg="white",
        padx=12,
        pady=4,
    ).grid(row=2, column=1, pady=12)

    root.mainloop()


if __name__ == "__main__":
    main()
