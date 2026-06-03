from flask import render_template
from app.main import bp

#landing page route
@bp.route('/')
def index():
    return render_template('index.html')
