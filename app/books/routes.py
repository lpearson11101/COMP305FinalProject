from flask import render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, func
from flask_login import current_user
from app.books import bp
from app.models.book import Book
from app.models.userbook import UserBook
from app.extensions import db


@bp.route('/', methods=('GET', 'POST'))
def index():
    books = Book.query.all()

    if request.method == 'POST':
        name = request.form.get("Book")
        info = request.form.get("Information")
        new_book = Book(name=request.form['book'],
                        info=request.form['information'])
        
        existing_book = Book.query.filter_by(name=name).first()

        if existing_book:
            return render_template("books/index.html", error="Book already added!")
        
        if not name or not info:
            return render_template("books/index.html", error="Book name and information are required!")
        
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('books.index'))
    
    return render_template('books/index.html', books=books)

@bp.route('/books')
def books():
    return render_template('books/search.html')

@bp.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return render_template('books/search_results.html', results=[], query='')

    search_pattern = f'%{query}%'
    results = Book.query.filter(
        or_(Book.title.ilike(search_pattern), Book.author.ilike(search_pattern))
    ).order_by(Book.isbn.desc()).limit(20).all()

    return render_template('books/search_results.html', results=results, query=query)


@bp.route('/<int:book_id>')
def detail(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('books/detail.html', book=book)

@bp.route('/rate_aura/<int:book_id>', methods=['POST'])
def rate_aura(book_id):
    rating = float(request.form.get('aura'))
    user_id = current_user.id
    entry = UserBook.query.filter_by(user_id=user_id, book_id=book_id).first()
    if not entry:
        entry = UserBook(user_id=user_id, book_id=book_id)
        db.session.add(entry)
    entry.aura = rating
    db.session.commit()
    update_book_averages(book_id)
    return redirect(url_for('books.detail', book_id=book_id))


@bp.route('/rate_enjoyment/<int:book_id>', methods=['POST'])
def rate_enjoyment(book_id):
    rating = float(request.form.get('enjoyment'))
    user_id = current_user.id
    entry = UserBook.query.filter_by(user_id=user_id, book_id=book_id).first()
    if not entry:
        entry = UserBook(user_id=user_id, book_id=book_id)
        db.session.add(entry)
    entry.enjoyment = rating
    db.session.commit()
    update_book_averages(book_id)
    return redirect(url_for('books.detail', book_id=book_id))


@bp.route('/mark_read/<int:book_id>', methods=['POST'])
def mark_read(book_id):
    user_id = current_user.id
    entry = UserBook.query.filter_by(user_id=user_id, book_id=book_id).first()
    if not entry:
        entry = UserBook(user_id=user_id, book_id=book_id)
        db.session.add(entry)
    entry.mark_read = True
    db.session.commit()
    return redirect(url_for('books.detail', book_id=book_id))


@bp.route('/mark_to_read/<int:book_id>', methods=['POST'])
def mark_to_read(book_id):
    user_id = current_user.id
    entry = UserBook.query.filter_by(user_id=user_id, book_id=book_id).first()
    if not entry:
        entry = UserBook(user_id=user_id, book_id=book_id)
        db.session.add(entry)
    entry.to_read = True
    db.session.commit()
    return redirect(url_for('books.detail', book_id=book_id))


@bp.route('/add_top_five/<int:book_id>', methods=['POST'])
def add_top_five(book_id):
    user_id = current_user.id
    entry = UserBook.query.filter_by(user_id=user_id, book_id=book_id).first()
    if not entry:
        entry = UserBook(user_id=user_id, book_id=book_id)
        db.session.add(entry)
    entry.top_five = 1  # placeholder rank
    db.session.commit()
    return redirect(url_for('books.detail', book_id=book_id))


def update_book_averages(book_id):
    aura_avg = db.session.query(func.avg(UserBook.aura)).filter(UserBook.book_id == book_id).scalar()
    enjoyment_avg = db.session.query(func.avg(UserBook.enjoyment)).filter(UserBook.book_id == book_id).scalar()
    book = Book.query.get(book_id)
    book.agg_aura = aura_avg or 0
    book.agg_enjoyment = enjoyment_avg or 0
    db.session.commit()

@bp.route('/unmark_read/<int:book_id>', methods=['POST'])
def unmark_read(book_id):
    user_id = current_user.id
    entry = UserBook.query.filter_by(user_id=user_id, book_id=book_id).first()
    if entry:
        entry.mark_read = False
        db.session.commit()
    return redirect(url_for('books.detail', book_id=book_id))


@bp.route('/remove_to_read/<int:book_id>', methods=['POST'])
def remove_to_read(book_id):
    user_id = current_user.id
    entry = UserBook.query.filter_by(user_id=user_id, book_id=book_id).first()
    if entry:
        entry.to_read = False
        db.session.commit()
    return redirect(url_for('books.detail', book_id=book_id))


@bp.route('/remove_top_five/<int:book_id>', methods=['POST'])
def remove_top_five(book_id):
    user_id = current_user.id
    entry = UserBook.query.filter_by(user_id=user_id, book_id=book_id).first()
    if entry:
        entry.top_five = None
        db.session.commit()
    return redirect(url_for('books.detail', book_id=book_id))

