from flask import render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from app.books import bp
from app.models.book import Book
from app.extensions import db


@bp.route('/', methods=('GET', 'POST'))
def index():
    books = Book.query.all()

    if request.method == 'POST':
        new_book = Book(name=request.form['book'],
                        info=request.form['information'])
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('books.index'))
    
    return render_template('books/index.html', books=books)

@bp.route('/search')
def search():
    query = request.args.get('q', '').strip()
    
    if not query:
        return render_template('search_results.html', 
                             results=[], 
                             query='')
    
    # Case-insensitive search in title and content
    search_pattern = f'%{query}%'
    results = Book.query.filter(
        db.or_(
            Book.name.ilike(search_pattern),
            Book.info.ilike(search_pattern)
        )
    ).order_by(Book.isbn.desc()).limit(20).all()
    
    return render_template('search_results.html', 
                         results=results, 
                         query=query)