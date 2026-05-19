from flask import (
    render_template,
    request,
    redirect,
    url_for
)

from flask_login import (
    login_required,
    login_user,
    logout_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from app.auth import bp
from app.extensions import db
from app.models.user import User

# Register route
@bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:
            return render_template(
                "auth/register.html",
                error="Username already taken!"
            )

        hashed_password = generate_password_hash(
            password,
            method="pbkdf2:sha256"
        )

        new_user = User(
            username=username,
            password_hash=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("auth.login"))
    return render_template("auth/register.html")

# Login route
@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(
            username=username
        ).first()

        if user and check_password_hash(
            user.password_hash,
            password
        ):
            login_user(user)
            return redirect(
                url_for("users.profile")
            )

        return render_template(
            "auth/login.html",
            error="Invalid username or password"
        )
    return render_template("auth/login.html")

# Logout route
@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))