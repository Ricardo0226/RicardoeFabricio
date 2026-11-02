import pytest

from app import create_app
from database import db
from models import Classroom, User


@pytest.fixture()
def client(tmp_path):
    database_path = tmp_path / "authorization.sqlite"
    test_app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-key",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path}",
        }
    )
    with test_app.app_context():
        classroom = Classroom(name="INFO4V", description="Turma ativa", active=True)
        users = [
            User(
                name="Estudante",
                email="aluno@example.com",
                role="student",
                classroom=classroom,
            ),
            User(
                name="Líder",
                email="lider@example.com",
                role="leader",
                classroom=classroom,
            ),
            User(
                name="Administrador",
                email="admin@example.com",
                role="admin",
                classroom=classroom,
            ),
        ]
        for user in users:
            user.set_password("senha-segura")
        db.session.add_all([classroom, *users])
        db.session.commit()
        yield test_app.test_client()
        db.drop_all()


def login(client, email):
    return client.post(
        "/login",
        data={"email": email, "password": "senha-segura"},
    )


def test_visitor_is_redirected_to_login_with_return_path(client):
    response = client.get("/admin")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login?next=/admin")


def test_student_is_blocked_from_administration(client):
    login(client, "aluno@example.com")

    response = client.get("/admin", follow_redirects=True)

    assert response.status_code == 200
    assert b"Apenas l\xc3\xadderes e administradores" in response.data
    assert b"Gerenciar compromissos" not in response.data


def test_leader_can_access_administration(client):
    login(client, "lider@example.com")

    response = client.get("/admin")

    assert response.status_code == 200
    assert b"Gerenciar compromissos" in response.data
    assert b"Novo compromisso" in response.data


def test_admin_can_access_administration(client):
    login(client, "admin@example.com")

    response = client.get("/admin")

    assert response.status_code == 200
    assert b"Gerenciar compromissos" in response.data


def test_navigation_shows_management_link_only_to_authorized_roles(client):
    visitor_home = client.get("/")
    assert b"Gerenciar eventos" not in visitor_home.data

    login(client, "aluno@example.com")
    student_home = client.get("/")
    assert b"Gerenciar eventos" not in student_home.data

    client.post("/logout")
    login(client, "lider@example.com")
    leader_home = client.get("/")
    assert b"Gerenciar eventos" in leader_home.data
