# User model
from app.extensions import db

class Book(db.Model):

    # A book's ID. Acts as the primary key
    id = db.Column(db.Integer, primary_key=True)

    # A book's title, chr limit of 250 and cannot be null
    title = db.Column(db.String(250), nullable=False)

    # A book's author, chr limit of 250 and cannot be null
    author = db.Column(db.String(250), nullable=False)

    # A book's publisher, chr limit of 250 and cannot be null
    publisher = db.Column(db.String(250), nullable=False)

    # A book's identifying ISBN, chr limit of 20, since ISBNs are roughly 17 chrs. 20 is for lenience. Must be unique.
    isbn = db.Column(db.String(20), unique=True)

    # The id of a book's cover, must be unique
    cover_id = db.Column(db.Integer, unique=True)

    # A book's summary
    summary = db.Column(db.Text)

    # The year a book was published
    year_published = db.Column(db.Integer)

    # A book's genre, chr limit of 250, cannot be null (could sub-in a genre like abstract if not known)
    genre = db.Column(db.String(250), nullable=False)

    # A description of how long a book would take to read. 
    length = db.Column(db.String(250))

    # The aggregated enjoyment rating
    agg_enjoyment = db.Column(db.Float)

    # The aggregated aura rating
    agg_aura = db.Column(db.Float, nullable=False)

    # The first "persona" assigned to a book, cannot be null
    persona_one = db.Column(db.String(250), nullable=False)

    # The second "persona" assigned to a book
    persona_two = db.Column(db.String(250))
    
    # The third "persona" assigned to a book
    persona_three = db.Column(db.String(250))