# Author-book model to keep track of the books written by an author account
from app.extensions import db

class AuthorBook(db.Model):
    __tablename__ = "author_books"
    # The ID of the author-book interaction. Acts as the primary key
    authorbook_id = db.Column(db.Integer, primary_key=True)

    # The author's user id
    author_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

     # The book's id
    book_id = db.Column(
        db.Integer,
        db.ForeignKey("books.id"),
        nullable=False
    )

    #Author relationship. authorbook.author returns <User>
    author = db.relationship(
        "User",
        back_populates="author_books"
    )

    #Book relationship. authorbook.book returns <Book>
    book = db.relationship(
        "Book",
        back_populates="author_books"
    )