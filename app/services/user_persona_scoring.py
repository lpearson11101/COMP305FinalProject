from app.extensions import db

from app.models.userbook import UserBook
from app.models.bookpersonaaggregate import BookPersonaAggregate
from app.models.userpersonaaggregate import UserPersonaAggregate


def recalculate_user_personas(user_id):

    UserPersonaAggregate.query.filter_by(
        user_id=user_id
    ).delete()

    persona_scores = {}

    top_five_books = (
        UserBook.query
        .filter(
            UserBook.user_id == user_id,
            UserBook.top_five.isnot(None)
        )
        .all()
    )

    for entry in top_five_books:

        top_five_weight = 6 - entry.top_five

        top_personas = (
            BookPersonaAggregate.query
            .filter_by(book_id=entry.book_id)
            .order_by(BookPersonaAggregate.score.desc())
            .limit(3)
            .all()
        )

        for rank, aggregate in enumerate(top_personas, start=1):

            persona_weight = 4 - rank

            score = top_five_weight * persona_weight

            persona_scores[aggregate.persona_id] = (
                persona_scores.get(
                    aggregate.persona_id,
                    0
                )
                + score
            )

    for persona_id, score in persona_scores.items():

        db.session.add(
            UserPersonaAggregate(
                user_id=user_id,
                persona_id=persona_id,
                score=score
            )
        )

    db.session.commit()

#get the user's top personas based on the aggregates
def get_top_user_personas(user_id, limit=3):
    """
    Retrieve the user's top personas based on calculated aggregates.
    
    Args:
        user_id: The ID of the user
        limit: Maximum number of personas to return (default: 3)
    
    Returns:
        List of UserPersonaAggregate objects ordered by score (descending),
        or empty list if no aggregates exist yet
    """
    return UserPersonaAggregate.query.filter_by(user_id=user_id).order_by(
        UserPersonaAggregate.score.desc()
    ).limit(limit).all()