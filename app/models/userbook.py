# User-book model
from app.extensions import db

class UserBook(db.Model):
    __tablename__ = "user_books"
    # The ID of the user-book interaction. Acts as the primary key
    id = db.Column(db.Integer, primary_key=True)

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
        nullable=False
    )

    # Is a book marked as read? True or False.
    mark_read = db.Column(db.Boolean, default=False)

    # Is a book in the user's 'to read' list? True or False check
    to_read = db.Column(db.Boolean, default=False)

    # What position in the user's top five is this book? Must be tested to ensure the book is in the top five
    top_five = db.Column(db.Integer)

    # What does the user rank this book? Must be tested to ensure the book was read   
    enjoyment = db.Column(db.Float)

    # What does the user rank the A.U.R.A of this book?
    aura = db.Column(db.Float)

    #User relationship. userbook.user returns <User>
    user = db.relationship(
        "User",
        back_populates="user_books"
    )

    #Book relationship. userbook.book returns <Book>
    book = db.relationship(
        "Book",
        back_populates="user_books"
    )

    #UserBookPersona relationship. If a user-book interaction is deleted, all associated personas are also deleted.
    personas = db.relationship(
    "UserBookPersona",
    back_populates="userbook",
    cascade="all, delete-orphan"
    )
    #a user can only have one user-book interaction per book, so we set a unique constraint on the combination of user_id and book_id
    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "book_id",
            name="unique_user_book"
        ),
    )