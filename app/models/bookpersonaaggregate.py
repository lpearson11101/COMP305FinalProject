# Book persona aggregate model for calculations
from app.extensions import db

class BookPersonaAggregate(db.Model):
    __tablename__ = "book_persona_aggregates"
    # A book_persona_aggregates's ID. Acts as the primary key
    id = db.Column(db.Integer, primary_key=True)

    #book_id is the foreign key to the books table, linking this aggregate to a specific book. It cannot be null.
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)

    #persona_id is the foreign key to the personas table, linking this aggregate to a specific persona. It cannot be null.
    persona_id = db.Column(db.Integer, db.ForeignKey('personas.id'), nullable=False)

    #that persona's score for that book. It is a floating-point number and cannot be null. Default value is 0.0, indicating no score has been calculated yet.
    score = db.Column(db.Float, nullable=False, default=0.0)

    #Book relationship. 
    book = db.relationship(
        "Book",
        back_populates="book_persona_aggregates"
    )

    #Persona relationship. 
    persona = db.relationship(
        "Persona",
        back_populates="book_persona_aggregates"
    )

    #a book can only have one aggregate per persona, so we set a unique constraint on the combination of book_id and persona_id
    __table_args__ = (
        db.UniqueConstraint(
            "book_id",
            "persona_id",
            name="unique_book_persona"
        ),
    )