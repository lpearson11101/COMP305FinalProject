from pathlib import Path

from flask import flash, render_template, request, url_for, redirect, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, func
from sqlalchemy.exc import IntegrityError
from flask_login import current_user, login_required
from app.books import bp
from app.forms.comment_form import CommentForm
from app.models.book import Book
from app.models.userbook import UserBook
from app.models.comment import Comment
from sqlalchemy.orm import joinedload
from app.extensions import db
from app.services.covers import ensure_cover_cached
from app.models.persona import Persona
from app.models.userbookpersona import UserBookPersona
from app.models.bookpersonaaggregate import BookPersonaAggregate
from app.services.persona_scoring import recalculate_book_personas
from app.services.user_persona_scoring import recalculate_user_personas

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
    page = request.args.get('page', 1, type=int)
    
    # Query all books with pagination
    paginated_books = Book.query.paginate(page=page, per_page=20)
    
    # Attach cover_path to each book
    for book in paginated_books.items:
        #check if book has a cover_id. if not, use default cover
        if book.cover_id:
            #check if the cover has been cached locally, if so use it, otherwise use default
            cover_file = f"covers/{book.cover_id}.jpg"
            full_path = Path("app/static") / cover_file
            if full_path.exists():
                book.cover_path = cover_file
            else:
                book.cover_path = "covers/default.jpg"
        else:
            book.cover_path = "covers/default.jpg"
    # Render the template with the paginated books
    return render_template('books/search.html', paginated_books=paginated_books)


#route to search for books by title or author. Uses ilike for case-insensitive partial matching. 
#Limits results to 20. Also attaches cover_path to each book for display in results.
@bp.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return render_template('books/search_results.html', results=[], query='')

    search_pattern = f'%{query}%'
    results = Book.query.filter(
        or_(Book.title.ilike(search_pattern), Book.author.ilike(search_pattern))
    ).order_by(Book.isbn.desc()).limit(20).all()

    # Attach cover_path like detail() does
    for book in results:
        if book.cover_id:
            cover_file = f"covers/{book.cover_id}.jpg"
            full_path = Path("app/static") / cover_file
            if full_path.exists():
                book.cover_path = cover_file
            else:
                book.cover_path = "covers/default.jpg"
        else:
            book.cover_path = "covers/default.jpg"

    return render_template(
        'books/search_results.html',
        results=results,
        query=query
    )

#Book detail page. Loads/renders the book and its comments. Handles comment submission
@bp.route('/books/<int:book_id>', methods=['GET', 'POST'])
def detail(book_id):
    book = Book.query.options(
        joinedload(Book.comments).joinedload(Comment.user)
    ).get_or_404(book_id)

    # Cover fetch only runs when page is visited
    cover_path = None
    if book.cover_id:
        cover_path = ensure_cover_cached(book.cover_id)

    #comments form
    form = CommentForm()

    #book and personas for dropdowns
    personas = Persona.query.all()

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You must be logged in to comment.")
            return redirect(url_for("auth.login"))

        comment = Comment(
            content=form.body.data,
            user=current_user,
            book=book
        )

        db.session.add(comment)
        db.session.commit()

        flash("Comment posted.", "success")
        return redirect(url_for("books.detail", book_id=book.id))
    
    #get top personas for this book
    top_personas = (
        BookPersonaAggregate.query
        .filter_by(book_id=book.id)
        .join(Persona)
        .order_by(BookPersonaAggregate.score.desc())
        .limit(3)
        .all()
    )

    current_personas = {}

    if current_user.is_authenticated:
        userbook = UserBook.query.filter_by(
            user_id=current_user.id,
            book_id=book.id
        ).first()

        if userbook:
            for p in userbook.personas:
                current_personas[p.ranking] = p.persona_id

    return render_template('books/detail.html', book=book, personas= personas, top_personas=top_personas, current_personas=current_personas, form=form, cover_path=cover_path)

#route for rating aura. Updates or creates a UserBook entry for the user and book, then updates the book's average ratings.
@bp.route('/rate_aura/<int:book_id>', methods=['POST'])
@login_required
def rate_aura(book_id):
    raw = request.form.get('aura')

    if not raw:
        flash("Please enter an A.U.R.A rating before submitting.", "danger")
        return redirect(url_for('books.detail', book_id=book_id))

    try:
        rating = float(raw)
    except ValueError:
        flash("Invalid A.U.R.A rating.", "danger")
        return redirect(url_for('books.detail', book_id=book_id))

    entry = UserBook.query.filter_by(user_id=current_user.id, book_id=book_id).first()
    if not entry:
        entry = UserBook(user_id=current_user.id, book_id=book_id)
        db.session.add(entry)

    entry.aura = rating
    db.session.commit()
    update_book_averages(book_id)

    return redirect(url_for('books.detail', book_id=book_id))


#route for rating enjoyment. Similar to aura route but updates enjoyment field instead
@bp.route('/rate_enjoyment/<int:book_id>', methods=['POST'])
@login_required
def rate_enjoyment(book_id):
    raw = request.form.get('enjoyment')

    if not raw:
        flash("Please enter an enjoyment rating before submitting.", "danger")
        return redirect(url_for('books.detail', book_id=book_id))

    try:
        rating = float(raw)
    except ValueError:
        flash("Invalid enjoyment rating.", "danger")
        return redirect(url_for('books.detail', book_id=book_id))

    entry = UserBook.query.filter_by(user_id=current_user.id, book_id=book_id).first()
    if not entry:
        entry = UserBook(user_id=current_user.id, book_id=book_id)
        db.session.add(entry)

    entry.enjoyment = rating
    db.session.commit()
    update_book_averages(book_id)

    return redirect(url_for('books.detail', book_id=book_id))

@bp.route('/mark_read/<int:book_id>', methods=['POST'])
@login_required
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
@login_required
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
@login_required
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
        flash("This book is already in your Top Five.", "info")
        return redirect(url_for('books.detail', book_id=book_id))

    # If full, do nothing
    if len(current_ranks) >= 5:
        flash("Your Top Five is already full. Remove a book first.", "danger")
        return redirect(url_for('books.detail', book_id=book_id))

    # Assign next available rank
    used_ranks = {e.top_five for e in current_ranks}
    for rank in range(1, 6):
        if rank not in used_ranks:
            entry.top_five = rank
            break

    db.session.commit()
    fix_top_five(user_id)
    recalculate_user_personas(user_id)

    flash("Added to Top Five.", "success")
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
@login_required
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
        recalculate_user_personas(user_id)
    
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
@login_required
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
        recalculate_user_personas(user_id)
    return redirect(url_for('users.profile'))


@bp.route('/top_five_down/<int:book_id>', methods=['POST'])
@login_required
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
        recalculate_user_personas(user_id)

    return redirect(url_for('users.profile'))

#route for editing comments
@bp.route("/comments/<int:comment_id>/edit", methods=["GET", "POST"])
@login_required
def edit_comment(comment_id):

    comment = Comment.query.get_or_404(comment_id)

    #don't allow users to edit other users' comments
    if comment.user_id != current_user.id:
        abort(403)

    form = CommentForm(obj=comment)

    #add the existing comment content to the form on GET so it shows up in the textarea for editing
    if request.method == "GET":
        form.body.data = comment.content


    if form.validate_on_submit():
        comment.content = form.body.data

        db.session.commit()

        flash("Comment updated.", "success")

        return redirect(
            url_for("books.detail", book_id=comment.book_id)
        )

    return render_template(
        "edit_comment.html",
        form=form,
        comment=comment
    )

#route for deleting comments
@bp.route("/comments/<int:comment_id>/delete", methods=["POST"])
@login_required
def delete_comment(comment_id):

    comment = Comment.query.get_or_404(comment_id)

    if comment.user_id != current_user.id:
        abort(403)

    book_id = comment.book_id

    db.session.delete(comment)
    db.session.commit()

    flash("Comment deleted.", "success")

    return redirect(
        url_for("books.detail", book_id=book_id)
    )
@bp.route('/admin/add', methods=['GET', 'POST'])
def admin_add_book():
    personas = Persona.query.all()
    if request.method == 'POST':
        isbn = request.form.get('isbn')

        if isbn == "":
            isbn = None
        # Normalize ISBN 
        elif isbn:
            isbn = isbn.strip()


        # Check isbn is unique before inserting
        existing_isbn = Book.query.filter_by(isbn=isbn).first()
        if isbn and existing_isbn:
            return render_template("books/admin_add.html", error="ISBN already exists", personas=personas)
        
        new_book = Book(
            title=request.form['title'],
            author=request.form['author'],
            publisher=request.form['publisher'],
            isbn=isbn,
            cover_id=None,
            summary=request.form.get('summary'),
            year_published=request.form.get('year_published'),
            genre=request.form.get('genre'),
            length=request.form.get('length'),
            agg_enjoyment=0.0,
            agg_aura=0.0,
        )
        db.session.add(new_book)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return render_template("books/admin_add.html", error="ISBN already exists", personas=personas)
        return redirect(url_for('books.detail', book_id=new_book.id))

    return render_template('books/admin_add.html', personas=personas)



@bp.route('/admin/delete/<int:book_id>', methods=['POST'])
def admin_delete_book(book_id):
    if current_user.role != 'admin':
        return "You're not fancy enough", 403

    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('books.search'))


#persona selection route. Updates the user's persona rankings for the book, then recalculates the book's aggregate persona scores.
@bp.route('/set_personas/<int:book_id>', methods=['POST'])
@login_required
def set_personas(book_id):
    user_id = current_user.id

    # Get or create UserBook entry
    entry = UserBook.query.filter_by(user_id=user_id, book_id=book_id).first()
    if not entry:
        entry = UserBook(user_id=user_id, book_id=book_id)
        db.session.add(entry)
        db.session.flush()

    # Clear old personas
    entry.personas.clear()
    db.session.flush()

    # Add new personas. Prevent duplicates
    selected = set()

    for i in range(1, 4):
        persona_id = request.form.get(f"persona_{i}")

        if not persona_id:
            continue

        if persona_id in selected:
            flash(
                "You cannot select the same persona more than once.",
                "danger"
            )
            return redirect(
                url_for('books.detail', book_id=book_id)
            )

        selected.add(persona_id)

        db.session.add(
            UserBookPersona(
                persona_id=int(persona_id),
                userbook_id=entry.id,
                ranking=i
            )
        )

    if not selected:
        flash(
            "Please select at least one persona.",
            "danger"
        )
        return redirect(
            url_for('books.detail', book_id=book_id)
        )

    db.session.commit()

    #recalculate aggregate persona scores for the book
    recalculate_book_personas(book_id)

    #recalculate user personas for the affected users after the book's personas change
    affected_userbooks = UserBook.query.filter_by(book_id=book_id).all()
    affected_user_ids = {ub.user_id for ub in affected_userbooks}
    for user_id in affected_user_ids:
        recalculate_user_personas(user_id)
    flash("Personas updated.", "success")

    return redirect(url_for('books.detail', book_id=book_id))
