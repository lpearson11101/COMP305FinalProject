from flask import render_template
from app.books import bp

@bp.route('/')
def index():
    return render_template('books/index.html')

