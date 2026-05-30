# User model
from flask_login import UserMixin

from app.extensions import db

from app.extensions import login_manager

class User(UserMixin, db.Model):
    __tablename__ = "users"
    #unique id for each user, acts as the primary key
    id = db.Column(db.Integer, primary_key=True)

    # The user's username, must be unique
    username = db.Column(db.String(250), unique=True, nullable=False)

    #the user's password, will be stored as a hash for security
    password_hash = db.Column(db.String(250), nullable=False)

    #whether the user is admin, author, or basic user, default is "user"
    role = db.Column(db.String(50), default="user")

    #User_Book relationship. If a user is deleted, all user-book interactions with that user are also deleted.
    #user.user_books returns a list of <UserBook> objects associated with that user
    user_books = db.relationship(
        "UserBook",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    author_books = db.relationship(
    "AuthorBook",
    back_populates="author",
    cascade="all, delete-orphan"
    )

    comments = db.relationship(
        "Comment",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    user_persona_aggregates = db.relationship(
        "UserPersonaAggregate",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    

