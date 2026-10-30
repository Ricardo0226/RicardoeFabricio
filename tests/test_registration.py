import pytest

from app import create_app
from database import db
from models import Classroom, User


@pytest.fixture()
def client(tmp_path):
    database_path = tmp_path / "registration.sqlite"
    test_app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-key",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path}",
        }
    )
    with test_app.app_context():
        db.session.add(Classroom(name="INFO4V", description="Turma ativa", active=True))
        db.session.commit()
        yield test_app.test_client()
        db.drop_all()


def test_registration_persists_student_with_hash_and_active_classroom(client):
    response = client.post(
        "/register",
        data={
            "name": "Ana Souza",
            "email": "ANA@EXAMPLE.COM",
            "password": "senha-segura",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Cadastro realizado com sucesso" in response.data
    with client.application.app_context():
        user = User.query.filter_by(email="ana@example.com").one()
        assert user.role == "student"
        assert user.classroom.name == "INFO4V"
        assert user.password_hash != "senha-segura"
        assert user.check_password("senha-segura")


def test_registration_rejects_duplicate_email(client):
    client.post(
        "/register",
        data={"name": "Ana Souza", "email": "ana@example.com", "password": "senha-segura"},
    )
    response = client.post(
        "/register",
        data={"name": "Outra Ana", "email": "ANA@EXAMPLE.COM", "password": "outra-senha"},
    )

    assert response.status_code == 400
    assert b"Este e-mail j\xc3\xa1 est\xc3\xa1 cadastrado" in response.data


def test_registration_rejects_invalid_data(client):
    response = client.post(
        "/register",
        data={"name": "A", "email": "email-invalido", "password": "123"},
    )

    assert response.status_code == 400
    assert b"Informe um nome" in response.data
    assert b"Informe um e-mail v\xc3\xa1lido" in response.data
    assert b"A senha deve ter pelo menos 8 caracteres" in response.data


def test_registration_requires_active_classroom(tmp_path):
    database_path = tmp_path / "without-classroom.sqlite"
    test_app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-key",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path}",
        }
    )
    response = test_app.test_client().post(
        "/register",
        data={"name": "Ana Souza", "email": "ana@example.com", "password": "senha-segura"},
    )

    assert response.status_code == 400
    assert b"N\xc3\xa3o h\xc3\xa1 turma ativa" in response.data
    with test_app.app_context():
        db.drop_all()
