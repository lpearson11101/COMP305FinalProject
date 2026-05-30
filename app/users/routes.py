from flask import render_template, request, url_for, redirect
from flask_login import login_required
from app.users import bp
from app.models.user import User

@bp.route("/profile")
@login_required
def profile():
    return render_template("users/profile.html")

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