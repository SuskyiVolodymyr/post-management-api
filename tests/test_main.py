from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from db.engine import Base
from db.models import User
from main import app, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


DEFAULT_POST_DATA = {
    "title": "test",
    "text": "test",
    "auto_reply": False,
    "auto_reply_time": 0,
}


@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client(db):
    with TestClient(app) as c:
        yield c


def create_test_user(client, email, password):
    user_data = {"email": email, "password": password}
    response = client.post("/register/", json=user_data)
    assert response.status_code == 201
    return response.json()


def get_auth_token(client, email, password):
    response = client.post("/token/", data={"username": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_user_registration(client, db):
    response = client.post("/register/", json={"email": "1@1.com", "password": "test"})
    assert response.status_code == 201
    assert response.json()["email"] == "1@1.com"

    db_user = db.query(User).filter(User.email == "1@1.com").first()
    assert db_user
    assert db_user.email == "1@1.com"
    assert db_user.hashed_password != "test"


def test_login(client):
    create_test_user(client, "1@1.com", "test")

    response = client.post("/token/", data={"username": "1@1.com", "password": "test"})
    assert response.status_code == 200
    assert response.json()["access_token"]
    assert response.json()["token_type"] == "bearer"


def test_get_posts(client):
    create_test_user(client, "1@1.com", "test")
    get_auth_token(client, "1@1.com", "test")

    response = client.get("/posts/")
    assert response.status_code == 200


def test_get_post_by_id(client):
    email = "1@1.com"
    password = "test"
    create_test_user(client, email, password)
    token = get_auth_token(client, email, password)

    client.post(
        "/posts/", json=DEFAULT_POST_DATA, headers={"Authorization": f"Bearer {token}"}
    )
    response = client.get("/posts/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["title"] == "test"
    assert response.json()["text"] == "test"
    assert response.json()["auto_reply"] is False
    assert response.json()["auto_reply_time"] == 0


def test_create_post(client):
    email = "1@1.com"
    password = "test"
    create_test_user(client, email, password)
    token = get_auth_token(client, email, password)

    response = client.post(
        "/posts/", json=DEFAULT_POST_DATA, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test title"
    assert response.json()["text"] == "Test text"
    assert response.json()["auto_reply"] is False
    assert response.json()["auto_reply_time"] == 0


def test_update_post(client):
    email = "1@1.com"
    password = "test"
    create_test_user(client, email, password)
    token = get_auth_token(client, email, password)

    post_update_data = {
        "title": "Updated Test title",
        "text": "Updated Test text",
        "auto_reply": False,
        "auto_reply_time": 0,
    }

    client.post(
        "/posts/", json=DEFAULT_POST_DATA, headers={"Authorization": f"Bearer {token}"}
    )

    response = client.put(
        "/posts/1", json=post_update_data, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    print(response.json())
    assert response.json()["title"] == "Updated Test title"
    assert response.json()["text"] == "Updated Test text"
    assert response.json()["auto_reply"] is False
    assert response.json()["auto_reply_time"] == 0


def test_delete_post(client):
    email = "1@1.com"
    password = "test"
    create_test_user(client, email, password)
    token = get_auth_token(client, email, password)

    client.post(
        "/posts/", json=DEFAULT_POST_DATA, headers={"Authorization": f"Bearer {token}"}
    )

    response = client.delete("/posts/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204


def test_get_comments(client):
    email = "1@1.com"
    password = "test"
    create_test_user(client, email, password)
    token = get_auth_token(client, email, password)

    response = client.get("/comments/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_create_comment(client):
    email = "1@1.com"
    password = "test"
    create_test_user(client, email, password)
    token = get_auth_token(client, email, password)

    client.post(
        "/posts/", json=DEFAULT_POST_DATA, headers={"Authorization": f"Bearer {token}"}
    )

    response = client.post(
        "/comments/",
        json={"text": "Test comment", "post_id": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201


def test_get_comments_with_post_id(client):
    email = "1@1.com"
    password = "test"
    create_test_user(client, email, password)
    token = get_auth_token(client, email, password)

    client.post(
        "/posts/", json=DEFAULT_POST_DATA, headers={"Authorization": f"Bearer {token}"}
    )
    client.post(
        "/posts/", json=DEFAULT_POST_DATA, headers={"Authorization": f"Bearer {token}"}
    )

    client.post(
        "/comments/",
        json={"text": "Test comment", "post_id": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        "/comments/",
        json={"text": "Test comment 2", "post_id": 2},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.get(
        "/comments/?post_id=2", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["text"] == "Test comment 2"


def test_get_comment_by_id(client):
    email = "1@1.com"
    password = "test"
    create_test_user(client, email, password)
    token = get_auth_token(client, email, password)

    client.post(
        "/posts/", json=DEFAULT_POST_DATA, headers={"Authorization": f"Bearer {token}"}
    )
    client.post(
        "/comments/",
        json={"text": "Test comment", "post_id": 1},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.get("/comments/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["text"] == "Test comment"


def test_update_comment(client):
    email = "1@1.com"
    password = "test"
    create_test_user(client, email, password)
    token = get_auth_token(client, email, password)

    client.post(
        "/posts/", json=DEFAULT_POST_DATA, headers={"Authorization": f"Bearer {token}"}
    )
    client.post(
        "/comments/",
        json={"text": "Test comment", "post_id": 1},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.put(
        "/comments/1",
        json={"text": "Updated Test comment", "post_id": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["text"] == "Updated Test comment"


def test_delete_comment(client):
    email = "1@1.com"
    password = "test"
    create_test_user(client, email, password)
    token = get_auth_token(client, email, password)

    client.post(
        "/posts/", json=DEFAULT_POST_DATA, headers={"Authorization": f"Bearer {token}"}
    )
    client.post(
        "/comments/",
        json={"text": "Test comment", "post_id": 1},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.delete(
        "/comments/1", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204


def test_auto_blocking_post(client):
    email = "1@1.com"
    password = "test"
    create_test_user(client, email, password)
    token = get_auth_token(client, email, password)
    post_data = {
        "title": "Test title",
        "text": "Fuck",
        "auto_reply": False,
        "auto_reply_time": 1,
    }
    response = client.post(
        "/posts/", json=post_data, headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    assert response.json()["is_blocked"] is True


def test_auto_blocking_comment(client):
    email = "1@1.com"
    password = "test"
    create_test_user(client, email, password)
    token = get_auth_token(client, email, password)
    comment_data = {"text": "Fuck", "post_id": 1}

    client.post(
        "/posts/", json=DEFAULT_POST_DATA, headers={"Authorization": f"Bearer {token}"}
    )
    response = client.post(
        "/comments/", json=comment_data, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    assert response.json()["is_blocked"] is True


def test_comments_analysis(client):
    email = "1@1.com"
    password = "test"
    create_test_user(client, email, password)
    token = get_auth_token(client, email, password)
    client.post(
        "/posts/", json=DEFAULT_POST_DATA, headers={"Authorization": f"Bearer {token}"}
    )
    client.post(
        "/comments/",
        json={"text": "Test comment 1", "post_id": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        "/comments/",
        json={"text": "Test comment 2", "post_id": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        "/comments/",
        json={"text": "Fuck", "post_id": 1},
        headers={"Authorization": f"Bearer {token}"},
    )

    date_from = datetime.today().strftime("%Y-%m-%d")
    date_to = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")

    response = client.get(
        f"/comments-daily-breakdown/?date_from={date_from}&date_to={date_to}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()[0]["day"] == date_from
    assert response.json()[0]["total_comments"] == 3
    assert response.json()[0]["blocked_comments"] == 1
