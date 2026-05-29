from flask import Blueprint

bp = Blueprint('books', __name__, template_folder='../templates/books')

from app.books import routes