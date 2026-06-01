# extract files from the Open Library dump to get a list of books and needed authors. 
# This is included here in case we need to add more books again later in the same way. This should not need to be run.

import gzip
import json
from pathlib import Path
import re

WORK_DUMP = Path("data/ol_dump_works_2026-04-30.txt.gz")

BOOKS_OUTPUT = Path("seed_data/books_raw.json")
AUTHORS_OUTPUT = Path("seed_data/needed_authors.json")

MAX_BOOKS = 2000

# get year of publication from book record
def extract_year(date_str):
    if not isinstance(date_str, str):
        return None

    match = re.search(r"(18|19|20)\d{2}", date_str)

    if match:
        return int(match.group(0))

    return None

books = []
needed_authors = set()
seen_titles = set()

with gzip.open(WORK_DUMP, "rt", encoding="utf-8") as f:

    for line in f:

        #split the line into parts to get the JSON record
        parts = line.split("\t")
        if len(parts) < 5:
            continue

        try:
            record = json.loads(parts[4])
        except json.JSONDecodeError:
            continue

        #make sure the book has a title, and retrieve it
        title = record.get("title")
        if not title:
            continue

        if title.lower() in seen_titles:
            continue

        seen_titles.add(title.lower())

        # id to get the book's cover_id
        covers = record.get("covers", [])
        cover_id = covers[0] if covers else None

        # skip books without covers
        if cover_id is None:
            continue

        # Description
        description = record.get("description")
        if isinstance(description, dict):
            description = description.get("value")
        elif not isinstance(description, str):
            description = None

        # genre (first subject according to Open Library)
        subjects = record.get("subjects", [])
        #only include books with at least one subject
        if not subjects:
            continue
        genre = subjects[0]

        # author
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

        # year published
        year = None
        first_publish_date = record.get("first_publish_date")

        # Skip records without a publication date
        if not first_publish_date:
            continue

        if first_publish_date is None:
            continue

        year = extract_year(first_publish_date)

        # append books
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
    json.dump(books, f, indent=2, ensure_ascii=False)

with open(AUTHORS_OUTPUT, "w", encoding="utf-8") as f:
    json.dump(sorted(list(needed_authors)), f, indent=2)

print(f"Saved {len(books)} books with covers")
print(f"Found {len(needed_authors)} authors")