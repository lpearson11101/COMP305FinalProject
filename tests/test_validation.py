import pytest
from app.models.user import User
from app.models.book import Book
from app.models.comment import Comment
from app.models.userbook import UserBook

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

#helper function to create a user
def make_user(username="user1"):
    return User(
        username=username,
        password_hash="hash",
        role="user"
    )

#helper function to create a book
def make_book(title="Book 1"):
    return Book(
        title=title,
        author="Author",
        publisher="Publisher",
        genre="Fantasy",
        agg_aura=0
    )

from app.books.routes import (
    fix_top_five,
    update_book_averages,
)

#test fix_top_five
def test_fix_top_five_reorders_ranks(app_context, db):
    #add a user and three books to the database
    user = make_user()

    book1 = make_book("Book 1")
    book2 = make_book("Book 2")
    book3 = make_book("Book 3")

    db.session.add_all([user, book1, book2, book3])
    db.session.commit()

    #add rankings to top five
    db.session.add_all([
        UserBook(
            user_id=user.id,
            book_id=book1.id,
            top_five=2
        ),
        UserBook(
            user_id=user.id,
            book_id=book2.id,
            top_five=4
        ),
        UserBook(
            user_id=user.id,
            book_id=book3.id,
            top_five=5
        ),
    ])
    db.session.commit()

    fix_top_five(user.id)

    rows = (
        UserBook.query
        .filter_by(user_id=user.id)
        .order_by(UserBook.top_five)
        .all()
    )
    #check correct order
    assert [r.top_five for r in rows] == [1, 2, 3]

#test update_book_averages
def test_update_book_averages(app_context, db):

    #add 2 users and a book to the database
    user1 = make_user("u1")
    user2 = make_user("u2")

    book = make_book("Dune")

    db.session.add_all([user1, user2, book])
    db.session.commit()

    #add ratings for the book from the two users
    db.session.add_all([
        UserBook(
            user_id=user1.id,
            book_id=book.id,
            aura=4,
            enjoyment=2,
        ),
        UserBook(
            user_id=user2.id,
            book_id=book.id,
            aura=2,
            enjoyment=4,
        ),
    ])
    db.session.commit()
    #update averages for the book based on ratings from the two users
    update_book_averages(book.id)

    db.session.refresh(book)

    #average ratings should be 3
    assert book.agg_aura == pytest.approx(3.0)
    assert book.agg_enjoyment == pytest.approx(3.0)

#test update_book_averages for the case where there are no ratings
def test_update_book_averages_no_ratings(app_context, db):
    book = make_book("Empty")

    db.session.add(book)
    db.session.commit()

    update_book_averages(book.id)

    db.session.refresh(book)

    assert book.agg_aura == 0
    assert book.agg_enjoyment == 0

#test default values when Userbook entry is created
def test_userbook_defaults(app_context, db):
    user = make_user()

    book = make_book("Defaults")

    db.session.add_all([user, book])
    db.session.commit()

    #create UserBook entry for user and book
    ub = UserBook(
        user_id=user.id,
        book_id=book.id
    )

    db.session.add(ub)
    db.session.commit()

    #check that the default values are as expected
    assert ub.mark_read is False
    assert ub.to_read is False
    assert ub.top_five is None
    assert ub.aura is None
    assert ub.enjoyment is None

#test that a book marked as top five is saved
def test_top_five_rank_saved(app_context, db):
    user = make_user()

    book = make_book("Top Five")

    db.session.add_all([user, book])
    db.session.commit()

    #create interaction between user and book, with book ranked "1" in top five
    ub = UserBook(
        user_id=user.id,
        book_id=book.id,
        top_five=1
    )

    db.session.add(ub)
    db.session.commit()

    #get the UserBook entry
    loaded = UserBook.query.first()

    #check that ranking is 1
    assert loaded.top_five == 1