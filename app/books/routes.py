from flask import render_template, request, url_for, redirect
from app.books import bp
from app.models.book import Book
from app.extensions import db


@bp.route('/', methods=('GET', 'POST'))
def index():
    books = Book.query.all()

    if request.method == 'POST':
        new_book = Book(content=request.form['book'],
                        answer=request.form['information'])
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('books.index'))
    
    return render_template('books/index.html', books=books)


