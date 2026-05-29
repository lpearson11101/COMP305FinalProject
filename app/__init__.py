from flask import Flask
from config import Config
from app.extensions import db, migrate, login_manager

def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(config_class)

    # init extensions
    db.init_app(app)
   
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"

    # register models so Alembic sees them
    from app import models

    migrate.init_app(app, db)

    # register blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.books import bp as books_bp
    app.register_blueprint(books_bp, url_prefix="/books")

    from app.users import bp as users_bp
    app.register_blueprint(users_bp, url_prefix="/users")

    return app