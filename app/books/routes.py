from flask import render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, func
from flask_login import current_user
from app.books import bp
from app.models.book import Book
from app.models.userbook import UserBook
from app.models.persona import Persona
from app.extensions import db
from app.models.userbookpersona import UserBookPersona


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
        return redirect(url_for('users.profile'))
    
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
    personas = Persona.query.all()
    return render_template('books/detail.html', book=book, personas=personas)

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

    # Find current max rank
    current_ranks = UserBook.query.filter(
        UserBook.user_id == user_id,
        UserBook.top_five.isnot(None)
    ).order_by(UserBook.top_five.asc()).all()

    # If already in top five, do nothing
    if entry.top_five:
        return redirect(url_for('books.detail', book_id=book_id))

    # If full, do nothing
    if len(current_ranks) >= 5:
        return redirect(url_for('books.detail', book_id=book_id))

    # Assign next available rank
    used_ranks = {e.top_five for e in current_ranks}
    for rank in range(1, 6):
        if rank not in used_ranks:
            entry.top_five = rank
            break

    db.session.commit()
    fix_top_five(user_id)

    return redirect(url_for('books.detail', book_id=book_id))

def fix_top_five(user_id):
    entries = UserBook.query.filter(
        UserBook.user_id == user_id,
        UserBook.top_five.isnot(None)
    ).order_by(UserBook.top_five.asc()).all()

    # Reassign ranks so th buttons work
    for i, entry in enumerate(entries, start=1):
        entry.top_five = i

    db.session.commit()

@bp.route('/unmark_read/<int:book_id>', methods=['POST'])
def unmark_read(book_id):
    user_id = current_user.id
    entry = UserBook.query.filter_by(user_id=user_id, book_id=book_id).first()
    if entry:
        entry.mark_read = False
        db.session.commit()
    return redirect(url_for('users.profile'))


@bp.route('/remove_to_read/<int:book_id>', methods=['POST'])
def remove_to_read(book_id):
    user_id = current_user.id
    entry = UserBook.query.filter_by(user_id=user_id, book_id=book_id).first()
    if entry:
        entry.to_read = False
        db.session.commit()
    return redirect(url_for('users.profile'))


@bp.route('/remove_top_five/<int:book_id>', methods=['POST'])
def remove_top_five(book_id):
    user_id = current_user.id
    entry = UserBook.query.filter_by(user_id=user_id, book_id=book_id).first()
    if entry:
        entry.top_five = None
        db.session.commit()
        fix_top_five(user_id)
    
    return redirect(url_for('users.profile'))

@bp.route('/admin/edit/<int:book_id>')
def admin_page(book_id):
    if current_user.role != 'admin':
        return "You're not fancy enough", 403

    book = Book.query.get_or_404(book_id)
    return render_template('books/admin_page.html', book=book)


@bp.route('/edit_book/<int:book_id>', methods=['POST'])
def edit_book(book_id):
    from flask_login import current_user

    if current_user.role != 'admin':
        return "You're not fancy enough", 403

    book = Book.query.get_or_404(book_id)
    
    book.title = request.form.get('title')
    book.author = request.form.get('author')
    book.publisher = request.form.get('publisher')
    book.year_published = request.form.get('year_published')
    book.isbn = request.form.get('isbn')
    book.length = request.form.get('length')
    book.cover_id = request.form.get('cover_id')
    book.genre = request.form.get('genre')
    book.summary = request.form.get('summary')

    db.session.commit()

    return redirect(url_for('books.detail', book_id=book.id))

def update_book_averages(book_id):
    aura_avg = db.session.query(func.avg(UserBook.aura)).filter(UserBook.book_id == book_id).scalar()
    enjoyment_avg = db.session.query(func.avg(UserBook.enjoyment)).filter(UserBook.book_id == book_id).scalar()
    book = Book.query.get(book_id)
    book.agg_aura = aura_avg or 0
    book.agg_enjoyment = enjoyment_avg or 0
    db.session.commit()

@bp.route('/top_five_up/<int:book_id>', methods=['POST'])
def top_five_up(book_id):
    user_id = current_user.id
    entry = UserBook.query.filter_by(user_id=user_id, book_id=book_id).first()

    if entry and entry.top_five and entry.top_five > 1:
        # Find the book currently above this one
        above = UserBook.query.filter_by(user_id=user_id, top_five=entry.top_five - 1).first()
        if above:
            above.top_five += 1
        entry.top_five -= 1
        db.session.commit()
        fix_top_five(user_id)
    return redirect(url_for('users.profile'))


@bp.route('/top_five_down/<int:book_id>', methods=['POST'])
def top_five_down(book_id):
    user_id = current_user.id

    entry = UserBook.query.filter_by(user_id=user_id, book_id=book_id).first()

    if not entry or entry.top_five is None:
        return redirect(url_for('books.top_five'))

    # Swap with the entry below it
    lower_entry = UserBook.query.filter_by(
        user_id=user_id,
        top_five=entry.top_five + 1
    ).first()

    if lower_entry:
        # Swap ranks
        entry.top_five, lower_entry.top_five = (
            lower_entry.top_five,
            entry.top_five
        )
        db.session.commit()
        fix_top_five(user_id)

    return redirect(url_for('users.profile'))

@bp.route('/admin/add', methods=['GET', 'POST'])
def admin_add_book():
    if request.method == 'POST':
        new_book = Book(
            title=request.form['title'],
            author=request.form['author'],
            publisher=request.form['publisher'],
            isbn=request.form.get('isbn'),
            cover_id=None,
            summary=request.form.get('summary'),
            year_published=request.form.get('year_published'),
            genre=request.form.get('genre'),
            length=request.form.get('length'),
            agg_enjoyment=0.0,
            agg_aura=0.0,
            persona_one=request.form.get('persona_one')
        )
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('books.admin_page'))

    personas = Persona.query.all()
    return render_template('books/admin_add.html', personas=personas)



@bp.route('/admin/delete/<int:book_id>', methods=['POST'])
def admin_delete_book(book_id):
    if current_user.role != 'admin':
        return "You're not fancy enough", 403

    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('books.search'))

@bp.route('/set_personas/<int:book_id>', methods=['POST'])
def set_personas(book_id):
    user_id = current_user.id

    # Get or create UserBook entry
    entry = UserBook.query.filter_by(user_id=user_id, book_id=book_id).first()
    if not entry:
        entry = UserBook(user_id=user_id, book_id=book_id)
        db.session.add(entry)
        db.session.commit()

    # Clear old personas
    entry.personas.clear()

    # Add new personas
    for i in range(1, 4):
        persona_id = request.form.get(f"persona_{i}")
        if persona_id:  # skip empty dropdowns
            persona = UserBookPersona(
                persona_id=int(persona_id),
                userbook_id=entry.id,
                ranking=i
            )
            db.session.add(persona)

    db.session.commit()
    return redirect(url_for('books.detail', book_id=book_id))
