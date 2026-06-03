from app.extensions import db

from app.models.userbook import UserBook
from app.models.bookpersonaaggregate import BookPersonaAggregate
from app.models.userpersonaaggregate import UserPersonaAggregate

#recalculate the user's persona aggregate scores based on their top five books and the persona aggregates for those books
def recalculate_user_personas(user_id):
    #remove existing aggregates for the user before recalculating
    UserPersonaAggregate.query.filter_by(
        user_id=user_id
    ).delete()

    persona_scores = {}

    #get the user's top five
    top_five_books = (
        UserBook.query
        .filter(
            UserBook.user_id == user_id,
            UserBook.top_five.isnot(None)
        )
        .all()
    )

    #get the top personas for the top five books
    for entry in top_five_books:

        top_five_weight = 6 - entry.top_five

        top_personas = (
            BookPersonaAggregate.query
            .filter_by(book_id=entry.book_id)
            .order_by(BookPersonaAggregate.score.desc())
            .limit(3)
            .all()
        )   

        #get the weights for the personas based on rank for the book
        for rank, aggregate in enumerate(top_personas, start=1):

            persona_weight = 4 - rank

            #multiply the weight based on rank in top 5 and persona rank for the book
            score = top_five_weight * persona_weight

            #add the score to the total for the persona, initializing if necessary
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
    #get the user's persona aggregates and return the top ones based on score
    return UserPersonaAggregate.query.filter_by(user_id=user_id).order_by(
        UserPersonaAggregate.score.desc()
    ).limit(limit).all()