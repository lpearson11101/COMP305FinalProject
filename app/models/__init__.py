from flask import Blueprint

bp = Blueprint('models', __name__)
from app.models.user import User
from app.models.book import Book
from app.models.userbook import UserBook
from app.models.comment import Comment
from app.models.persona import Persona
from app.models.userbookpersona import UserBookPersona
from app.models.bookpersonaaggregate import BookPersonaAggregate
from app.models.userpersonaaggregate import UserPersonaAggregate
from app.models.authorbook import AuthorBook