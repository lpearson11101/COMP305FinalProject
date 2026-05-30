# User-book-persona model
from app.extensions import db

class UserBookPersona(db.Model):
    __tablename__ = "user_book_personas"
    # The ID of the user-book-persona interaction. Acts as the primary key
    id = db.Column(db.Integer, primary_key=True)

    # The user-book interaction's id, must be unique
    userbook_id = db.Column(
        db.Integer,
        db.ForeignKey("user_books.id"),
        nullable=False
    )

    # The persona's id, must be unique
    persona_id = db.Column(
        db.Integer,
        db.ForeignKey("personas.id"),
        nullable=False
    )

    #the ranking of this persona for this user-book interaction. 
    ranking = db.Column(db.Integer)

    #User-book relationship. If a user-book interaction is deleted, all associated userbook_personas are also deleted.
    userbook = db.relationship(
        "UserBook",
<<<<<<< HEAD
        back_populates="user_book_personas",
=======
        back_populates="personas",
>>>>>>> e6f9731bda3722f5b0995f8d0f940facefa5c828
    )

    #Persona relationship. userbookpersona.persona returns <Persona>
    persona = db.relationship(
        "Persona",
        back_populates="user_book_personas"
    )