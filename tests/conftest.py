import pytest
from app import create_app
from app.extensions import db as _db

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
        _db.create_all()
        print(app.url_map)
        yield app
        # Clean up after test
        _db.session.remove()
        _db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def db():
    return _db

@pytest.fixture
def app_context(app):
    with app.app_context():
        yield