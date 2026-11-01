import pytest

from app import create_app
from database import db
from models import Classroom, User


@pytest.fixture()
def client(tmp_path):
    database_path = tmp_path / "login.sqlite"
    test_app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-key",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path}",
        }
    )
    with test_app.app_context():
        classroom = Classroom(name="INFO4V", description="Turma ativa", active=True)
        user = User(
            name="Ana Souza",
            email="ana@example.com",
            role="student",
            classroom=classroom,
        )
        user.set_password("senha-segura")
        db.session.add_all([classroom, user])
        db.session.commit()
        yield test_app.test_client()
        db.drop_all()


def test_valid_login_creates_session_and_redirects_to_calendar(client):
    response = client.post(
        "/login",
        data={"email": "ANA@EXAMPLE.COM", "password": "senha-segura"},
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")
    with client.session_transaction() as session:
        assert session["user_name"] == "Ana Souza"
        assert session["user_role"] == "student"
        assert "password" not in session

    home = client.get("/")
    assert home.status_code == 200
    assert b"Ola, Ana Souza" in home.data or "Olá, Ana Souza".encode() in home.data


def test_invalid_login_does_not_create_session(client):
    response = client.post(
        "/login",
        data={"email": "ana@example.com", "password": "senha-incorreta"},
    )

    assert response.status_code == 401
    assert b"E-mail ou senha inv\xc3\xa1lidos" in response.data
    with client.session_transaction() as session:
        assert "user_id" not in session


def test_logout_clears_session(client):
    client.post(
        "/login",
        data={"email": "ana@example.com", "password": "senha-segura"},
    )
    response = client.post("/logout", follow_redirects=True)

    assert response.status_code == 200
    assert b"Logout realizado com sucesso" in response.data
    with client.session_transaction() as session:
        assert not session


def test_calendar_remains_public_for_visitors(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"ClassSync" in response.data
