# User persona aggregate model for calculations
from app.extensions import db

class UserPersonaAggregate(db.Model):
    __tablename__ = "user_persona_aggregates"
    # A user_persona_aggregates's ID. Acts as the primary key
    id = db.Column(db.Integer, primary_key=True)

    #user_id is the foreign key to the users table, linking this aggregate to a specific user. It cannot be null.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    #persona_id is the foreign key to the personas table, linking this aggregate to a specific persona. It cannot be null.
    persona_id = db.Column(db.Integer, db.ForeignKey('personas.id'), nullable=False)

    #that persona's score for that user. It is a floating-point number and cannot be null. Default value is 0.0, indicating no score has been calculated yet.  
    score = db.Column(db.Float, nullable=False, default=0.0)

    #User relationship. 
    user = db.relationship(
        "User",
        back_populates="user_persona_aggregates"
    )

    #Persona relationship. 
    persona = db.relationship(
        "Persona",
        back_populates="user_persona_aggregates"
    )

    #a user can only have one aggregate per persona, so we set a unique constraint on the combination of user_id and persona_id
    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "persona_id",
            name="unique_user_persona"
        ),
    )
