from flask import Blueprint

bp = Blueprint('models', __name__)


from .user import User
from .book import Book
from .userbook import UserBook
from .authorbook import AuthorBook
from .comment import Comment
from .persona import Persona
from .userbookpersona import UserBookPersona
from .bookpersonaaggregate import BookPersonaAggregate
from .userpersonaaggregate import UserPersonaAggregate