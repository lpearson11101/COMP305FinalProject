# Comment model
from datetime import datetime

from app.extensions import db

class Comment(db.Model):
    __tablename__ = "comments"
    # A comment's ID. Acts as the primary key
    id = db.Column(db.Integer, primary_key=True)

    # A comment's content, chr limit of 1000 and cannot be null
    content = db.Column(db.String(1000), nullable=False)

    # The user's id
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

     # The book's id
    book_id = db.Column(
        db.Integer,
        db.ForeignKey("books.id"),
        nullable=False,
        index=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        index=True
    )

    #whether or not the comment was left by the author of the book. True or False check.
    author_comment = db.Column(db.Boolean, default=False)

    #User relationship. comment.user returns <User>
    user = db.relationship(
        "User",
        back_populates="comments"
    )

    #Book relationship. comment.book returns <Book>
    book = db.relationship(
        "Book",
        back_populates="comments"
    )