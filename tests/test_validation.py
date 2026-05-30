#these tests post invalid payloads and confirm the app re-renders the form w/ inline error indicators
import pytest


#register route tests

#test for registration with invalid password (too short)
def test_registration_invalid_password(client):
    response = client.post("register", data={
        "username": "testuser",
        "password": "short"
    }, follow_redirects=True)
    print(response.data.decode())
    assert b"at least 8 characters" in response.data

#test for registration with missing username
def test_registration_missing_username(client):
    response = client.post("register", data={
        "username": "",
        "password": "ValidPass1!"
    }, follow_redirects=True)
    print(response.data.decode())
    assert b"Username and password are required!" in response.data

#test for registration with missing password
def test_registration_missing_password(client):
    response = client.post("register", data={
        "username": "testuser",
        "password": ""
    }, follow_redirects=True)
    print(response.data.decode())
    assert b"Username and password are required!" in response.data

#test for registration with duplicate username
from app.models.user import User
def test_duplicate_user_registration(client, db):
    client.post("/register", data={
        "username": "testuser",
        "password": "Password123!"
    })

    response = client.post("/register", data={
        "username": "testuser",
        "password": "Password456!"
    })

    assert b"Username already taken!" in response.data


#test comment creation in database
from app.models.user import User
from app.models.book import Book
from app.models.comment import Comment


def test_create_comment(app_context, db):
    user = User(username="u1", password_hash="x")
    book = Book(
        title="Dune",
        author="Frank Herbert",
        publisher="Test",
        genre="Sci-Fi",
        agg_aura=0.0,
        persona_one="test"
    )

    db.session.add_all([user, book])
    db.session.commit()

    comment = Comment(
        content="Great book",
        user_id=user.id,
        book_id=book.id
    )

    db.session.add(comment)
    db.session.commit()

    assert Comment.query.count() == 1


#testing UserBook database relationship
from app.models.userbook import UserBook
from app.models.user import User
from app.models.book import Book


def test_userbook_relationship(app_context, db):
    user = User(username="u1", password_hash="x")
    book = Book(
        title="Dune",
        author="Frank Herbert",
        publisher="Test",
        genre="Sci-Fi",
        agg_aura=0.0,
        persona_one="test"
    )

    db.session.add_all([user, book])
    db.session.commit()

    ub = UserBook(user_id=user.id, book_id=book.id, mark_read=True)

    db.session.add(ub)
    db.session.commit()

    assert user.user_books[0].book_id == book.id
    assert book.user_books[0].user_id == user.id

#test UserBook unique constraint
from sqlalchemy.exc import IntegrityError
from app.models.userbook import UserBook


def test_userbook_unique_constraint(app_context, db):
    user = User(username="u1", password_hash="x")
    book = Book(
        title="Dune",
        author="Frank Herbert",
        publisher="Test",
        genre="Sci-Fi",
        agg_aura=0.0,
        persona_one="test"
    )

    db.session.add_all([user, book])
    db.session.commit()

    db.session.add(UserBook(user_id=user.id, book_id=book.id))
    db.session.commit()

    duplicate = UserBook(user_id=user.id, book_id=book.id)
    db.session.add(duplicate)

    with pytest.raises(IntegrityError):
        db.session.commit()