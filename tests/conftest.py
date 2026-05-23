import pytest
from app import create_app
from app.extensions import db

@pytest.fixture()
def app():
    # Create a test instance of the Flask app with in-memory SQLite database
    app = create_app()
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',  # Use in-memory database for tests
        WTF_CSRF_ENABLED=False,  # disable CSRF for easier form posts
    )
    
    with app.app_context():
        # Create all database tables
        db.create_all()
        print(app.url_map)
        yield app
        # Clean up after test
        db.session.remove()
        db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client()