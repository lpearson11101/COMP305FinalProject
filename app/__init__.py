from flask import Flask

from config import Config

from app.extensions import (
    db,
    migrate,
    login_manager
)


def create_app(config_class=Config):

    app = Flask(__name__)

    app.config.from_object(config_class)

    print(app)
    print(type(app))

    # Initialize extensions
    db.init_app(app)

    migrate.init_app(app, db)

    login_manager.init_app(app)

    login_manager.login_view = "auth.login"

    from app.models import user
    from app.auth import user_loader
    from app.models.book import Book
    from app.models.userbook import UserBook

    # Register blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.books import bp as books_bp
    app.register_blueprint(
        books_bp,
        url_prefix="/books"
    )

    from app.users import bp as users_bp
    app.register_blueprint(
        users_bp,
        url_prefix="/users"
    )

    return app