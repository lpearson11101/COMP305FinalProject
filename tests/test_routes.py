# route smoke tests to make sure key pages render

#testing the home page route
def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome" in response.data  

#testing the register page route
def test_register_user(client, db):
    response = client.post("/register", data={
        "username": "testuser",
        "password": "Password123!"
    }, follow_redirects=True)

    assert response.status_code == 200

#testing user account creation
from app.models.user import User
def test_register_creates_user(client, db):
    client.post("/register", data={
        "username": "testuser",
        "password": "Password123!"
    })

    user = User.query.filter_by(username="testuser").first()

    assert user is not None
    assert user.username == "testuser"


#testing login functionality
def test_login(client, db):
    client.post("/register", data={
        "username": "testuser",
        "password": "Password123!"
    })

    response = client.post("/login", data={
        "username": "testuser",
        "password": "Password123!"
    }, follow_redirects=True)

    assert response.status_code == 200

#testing the flask-login user loader
from app.models.user import User
from flask_login import current_user


def test_user_loader(client, db):
    from werkzeug.security import generate_password_hash
    user = User(
        username="u1",
        password_hash=generate_password_hash("Password123!")
    )
    db.session.add(user)
    db.session.commit()

    with client:
        client.post("/login", data={
            "username": "u1",
            "password": "Password123!"
        })

        assert current_user.is_authenticated