# Persona model
from app.extensions import db

class Persona(db.Model):
    __tablename__ = "personas"
    # A persona's ID. Acts as the primary key
    id = db.Column(db.Integer, primary_key=True)

    # A persona's name, chr limit of 250 and cannot be null
    name = db.Column(db.String(250), nullable=False)

    # A persona's description, chr limit of 1000 and cannot be null
    description = db.Column(db.String(1000), nullable=False)

