# User model
from app.extensions import db

class Book(db.Model):

    # A book's ID. Acts as the primary key
    userbook_id = db.Column(db.Integer, primary_key=True)

    # The user's id, must be unique
    user_id = db.Column(db.Integer, unique=True)

     # The book's id, must be unique
    book_id = db.Column(db.Integer, unique=True)

    # Is a book marked as read? True or False.
    mark_read = db.Column(db.Boolean)

    # Is a book in the user's 'to read' list? True or False check
    to_read = db.Column(db.Boolean)

    # What position in the user's top five is this book? Must be tested to ensure the book is in the top five
    top_five = db.Column(db.Integer)

    # What does the user rank this book? Must be tested to ensure the book was read   
    enjoyment = db.Column(db.float)

    # What does the user rank the A.U.R.A of this book?
    aura = db.Column(db.float)