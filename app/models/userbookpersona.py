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
        back_populates="personas",
    )

    #Persona relationship. userbookpersona.persona returns <Persona>
    persona = db.relationship(
        "Persona",
        back_populates="user_book_personas"
    )

    #unique constraint to ensure that a user-book interaction can only have one of each persona
    __table_args__ = (
        db.UniqueConstraint('userbook_id', 'persona_id', name='unique_userbook_persona'),
    )

    #unique constraint to ensure that a user-book interaction can only have one persona with a given ranking (can't have two personas both ranked 1)
    db.UniqueConstraint(
        "userbook_id",
        "ranking",
        name="unique_rank_per_userbook"
    )