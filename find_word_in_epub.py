import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

SEARCH_TERM = "word"
EPUB_DIR = "C:\\Users\\david\\OneDrive\\Documents\\ebooks"  # Change this to your epub folder path


def search_epub(filepath: str, term: str) -> list[str]:
    matches = []
    try:
        book = epub.read_epub(filepath)
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            soup = BeautifulSoup(item.get_content(), "html.parser")
            text = soup.get_text()
            for line in text.splitlines():
                if term.lower() in line.lower():
                    matches.append(line.strip())
    except Exception as e:
        print(f"Could not read {filepath}: {e}")
    return matches


def main():
    for filename in os.listdir(EPUB_DIR):
        if filename.endswith(".epub"):
            filepath = os.path.join(EPUB_DIR, filename)
            matches = search_epub(filepath, SEARCH_TERM)
            if matches:
                print(f"\n--- {filename} ---")
                for match in matches:
                    print(f"  {match}")


if __name__ == "__main__":
    main()