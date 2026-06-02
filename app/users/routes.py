from flask import render_template, request, url_for, redirect
from flask_login import login_required
from flask_login import current_user
from app.users import bp
from app.models.user import User
from app.models.userbook import UserBook
from app.services.user_persona_scoring import get_top_user_personas


@bp.route("/profile")
@login_required
def profile():
    user_id = current_user.id

    read_books = UserBook.query.filter_by(user_id=user_id, mark_read=True).all()
    to_read_books = UserBook.query.filter_by(user_id=user_id, to_read=True).all()
    top_five_books = UserBook.query.filter(
        UserBook.user_id == user_id,
        UserBook.top_five.isnot(None)
    ).order_by(UserBook.top_five.asc()).all()

    top_three_personas = get_top_user_personas(user_id, limit=3)

    return render_template(
        "users/profile.html",
        read_books=read_books,
        to_read_books=to_read_books,
        top_five_books=top_five_books,
        top_three_personas=top_three_personas
    )


@bp.route('/users')
def users():
    return render_template('users/user_search.html')

@bp.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return render_template('users/user_search_results.html', results=[], query='')

    search_pattern = f'%{query}%'
    results = User.query.filter(
        (User.username.ilike(search_pattern))
    ).order_by(User.username.desc()).limit(20).all()

    return render_template('users/user_search_results.html', results=results, query=query)

@bp.route('/user/<int:user_id>')
def user_details(user_id):
    user = User.query.get_or_404(user_id)

    top_five = UserBook.query.filter_by(user_id=user_id)\
                             .filter(UserBook.top_five.isnot(None))\
                             .order_by(UserBook.top_five.asc()).all()

    to_read = UserBook.query.filter_by(user_id=user_id, to_read=True).all()
    read = UserBook.query.filter_by(user_id=user_id, mark_read=True).all()
    top_three_personas = get_top_user_personas(user_id, limit=3)

    return render_template('users/user_details.html',
                           user=user,
                           top_five=top_five,
                           to_read=to_read,
                           read=read,
                           top_three_personas=top_three_personas)
