# extract files from the Open Library dump to get a list of books and needed authors. 
# This is included here in case we need to add more books again later in the same way. This should not need to be run.

import gzip
import json
from pathlib import Path

WORK_DUMP = Path("data/ol_dump_works_2026-04-30.txt.gz")

BOOKS_OUTPUT = Path("seed_data/books_raw.json")
AUTHORS_OUTPUT = Path("seed_data/needed_authors.json")

MAX_BOOKS = 2000

books = []
needed_authors = set()
seen_titles = set()

with gzip.open(WORK_DUMP, "rt", encoding="utf-8") as f:

    for line in f:

        parts = line.split("\t")

        if len(parts) < 5:
            continue

        try:
            record = json.loads(parts[4])
        except json.JSONDecodeError:
            continue

        title = record.get("title")

        if not title:
            continue

        if title.lower() in seen_titles:
            continue

        seen_titles.add(title.lower())

        # Description

        description = record.get("description")

        if isinstance(description, dict):
            description = description.get("value")

        elif not isinstance(description, str):
            description = None

        # Genre

        subjects = record.get("subjects", [])

        genre = (
            subjects[0]
            if subjects
            else "General"
        )

        # Cover

        covers = record.get("covers", [])

        cover_id = covers[0] if covers else None

        # Author key

        author_key = None

        work_authors = record.get("authors", [])

        if work_authors:

            author_key = (
                work_authors[0]
                .get("author", {})
                .get("key")
            )

            if author_key:
                needed_authors.add(author_key)

        # Publish year

        year = None

        first_publish_date = record.get(
            "first_publish_date"
        )

        if first_publish_date:

            digits = "".join(
                c for c in first_publish_date
                if c.isdigit()
            )

            if len(digits) >= 4:
                year = int(digits[:4])

        books.append({
            "title": title,
            "author_key": author_key,
            "publisher": "Unknown",
            "isbn": None,
            "cover_id": cover_id,
            "summary": description,
            "year_published": year,
            "genre": genre,
            "agg_aura": 0.0,
            "persona_one": None,
            "persona_two": None,
            "persona_three": None
        })

        if len(books) >= MAX_BOOKS:
            break

BOOKS_OUTPUT.parent.mkdir(exist_ok=True)

with open(BOOKS_OUTPUT, "w", encoding="utf-8") as f:
    json.dump(
        books,
        f,
        indent=2,
        ensure_ascii=False
    )

with open(AUTHORS_OUTPUT, "w", encoding="utf-8") as f:
    json.dump(
        sorted(list(needed_authors)),
        f,
        indent=2
    )

print(f"Saved {len(books)} books")
print(f"Need {len(needed_authors)} authors")