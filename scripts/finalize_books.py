#replacing author keys with actual author names based on build_author_lookup
#books are added to books.json
#This is included here in case we need to add more books again later in the same way. This should not need to be run.

import json
from pathlib import Path

BOOKS_INPUT = Path(
    "seed_data/books_raw.json"
)

AUTHOR_LOOKUP = Path(
    "seed_data/author_lookup.json"
)

OUTPUT_FILE = Path(
    "seed_data/books.json"
)

with open(
    BOOKS_INPUT,
    encoding="utf-8"
) as f:
    books = json.load(f)

with open(
    AUTHOR_LOOKUP,
    encoding="utf-8"
) as f:
    authors = json.load(f)

for book in books:

    book["author"] = authors.get(
        book["author_key"],
        "Unknown"
    )

    del book["author_key"]

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        books,
        f,
        indent=2,
        ensure_ascii=False
    )

print(
    f"Saved {len(books)} finalized books"
)