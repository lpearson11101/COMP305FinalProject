# This script builds a lookup table of author keys to author names, based on the needed authors from the previous step. This is used to get the author names for the final output.
# This is included here in case we need to add more books again later in the same way. This should not need to be run.

import gzip
import json
from pathlib import Path

AUTHOR_DUMP = Path(
    "data/ol_dump_authors_2026-04-30.txt.gz"
)

NEEDED_AUTHORS = Path(
    "seed_data/needed_authors.json"
)

OUTPUT_FILE = Path(
    "seed_data/author_lookup.json"
)

with open(
    NEEDED_AUTHORS,
    encoding="utf-8"
) as f:

    needed_authors = set(
        json.load(f)
    )

lookup = {}
remaining = len(needed_authors)

with gzip.open(
    AUTHOR_DUMP,
    "rt",
    encoding="utf-8"
) as f:

    for line in f:

        if remaining == 0:
            break

        parts = line.split("\t")

        if len(parts) < 5:
            continue

        try:
            record = json.loads(parts[4])
        except json.JSONDecodeError:
            continue

        key = record.get("key")

        if key not in needed_authors:
            continue

        lookup[key] = record.get(
            "name",
            "Unknown"
        )

        remaining -= 1

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        lookup,
        f,
        indent=2,
        ensure_ascii=False
    )

print(
    f"Saved {len(lookup)} authors"
)