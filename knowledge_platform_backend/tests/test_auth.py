import pytest
from fastapi.testclient import TestClient
from main import app  # assuming your FastAPI app is in main.py

client = TestClient(app)

def test_login_admin_success():
    res = client.post("/login", json={"username": "admin", "password": "password"})
    assert res.status_code == 200
    assert res.json()["role"] == "admin"
    assert "jwt=" in res.headers["set-cookie"]

def test_login_invalid_credentials():
    res = client.post("/login", json={"username": "wrong", "password": "bad"})
    assert res.status_code == 401

def test_me_authenticated():
    # First login
    res = client.post("/login", json={"username": "admin", "password": "password"})
    cookie = res.headers["set-cookie"]

    # Then call /me with cookie
    res2 = client.get("/me", headers={"Cookie": cookie})
    assert res2.status_code == 200
    assert res2.json()["role"] == "admin"

def test_me_unauthenticated():
    res = client.get("/me")
    assert res.status_code == 401
