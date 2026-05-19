from flask import render_template
from flask_login import login_required
from app.users import bp

@bp.route("/profile")
@login_required
def profile():
    return render_template("users/profile.html")