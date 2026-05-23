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

