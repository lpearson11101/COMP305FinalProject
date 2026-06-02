from app.models.book import Book
from app.models.bookpersonaaggregate import BookPersonaAggregate
from app.models.userbookpersona import UserBookPersona
from app.models.userbook import UserBook
from app.models.persona import Persona
from app.extensions import db


def recalculate_book_personas(book_id):
    """
    Recalculate aggregate persona scores for a book.

    Ranking weights:
        1st place = 3 points
        2nd place = 2 points
        3rd place = 1 point

    Also updates:
        book.persona_one
        book.persona_two
        book.persona_three
    """

    # Remove old aggregate rows
    BookPersonaAggregate.query.filter_by(
        book_id=book_id
    ).delete()

    persona_scores = {}

    # Get all persona rankings for this book
    rankings = (
        db.session.query(UserBookPersona)
        .join(UserBook)
        .filter(UserBook.book_id == book_id)
        .all()
    )

    for ranking in rankings:

        points = 4 - ranking.ranking

        persona_scores[ranking.persona_id] = (
            persona_scores.get(ranking.persona_id, 0)
            + points
        )

    # Recreate aggregate rows
    for persona_id, score in persona_scores.items():

        db.session.add(
            BookPersonaAggregate(
                book_id=book_id,
                persona_id=persona_id,
                score=score
            )
        )

    # Update book top-three personas
    book = Book.query.get(book_id)

    # Reset values first
    book.persona_one = None
    book.persona_two = None
    book.persona_three = None

    top_personas = (
        db.session.query(BookPersonaAggregate)
        .filter_by(book_id=book_id)
        .order_by(BookPersonaAggregate.score.desc())
        .limit(3)
        .all()
    )

    if len(top_personas) > 0:
        persona = Persona.query.get(top_personas[0].persona_id)
        book.persona_one = persona.name

    if len(top_personas) > 1:
        persona = Persona.query.get(top_personas[1].persona_id)
        book.persona_two = persona.name

    if len(top_personas) > 2:
        persona = Persona.query.get(top_personas[2].persona_id)
        book.persona_three = persona.name

    db.session.commit()