#loading books from books.json into the database.

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import json

from app import create_app
from app.extensions import db
from app.models import Book



app = create_app()

with app.app_context():

    with open(
        "seed_data/books.json",
        encoding="utf-8"
    ) as f:

        books = json.load(f)

    count = 0

    for book_data in books:

        existing = Book.query.filter_by(
            title=book_data["title"]
        ).first()

        if existing:
            continue

        book = Book(**book_data)

        db.session.add(book)

        count += 1

    db.session.commit()

    print(
        f"Loaded {count} books"
    )