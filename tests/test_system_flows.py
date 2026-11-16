from datetime import datetime

import pytest

from app import create_app
from database import db
from models import Classroom, Event, User


@pytest.fixture()
def system_client(tmp_path):
    database_path = tmp_path / "system.sqlite"
    test_app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "system-test-key",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path}",
        }
    )
    with test_app.app_context():
        classroom = Classroom(name="INFO4V", description="Turma ativa", active=True)
        users = [
            User(
                name="Estudante Sistema",
                email="student.system@example.com",
                role="student",
                classroom=classroom,
            ),
            User(
                name="Líder Sistema",
                email="leader.system@example.com",
                role="leader",
                classroom=classroom,
            ),
            User(
                name="Administrador Sistema",
                email="admin.system@example.com",
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


def event_data(**overrides):
    data = {
        "title": "Entrega do projeto integrador",
        "description": "Envio da documentação final",
        "category": "Trabalho",
        "start_at": "2026-11-20T19:00",
        "end_at": "2026-11-20T21:00",
    }
    data.update(overrides)
    return data


def test_visitor_can_view_calendar_and_events_but_not_manage_them(system_client):
    with system_client.application.app_context():
        db.session.add(
            Event(
                title="Aula pública",
                category="Evento",
                start_at=datetime(2026, 11, 20, 19, 0),
                end_at=datetime(2026, 11, 20, 21, 0),
            )
        )
        db.session.commit()

    calendar = system_client.get("/")
    events = system_client.get("/api/events")
    admin = system_client.get("/admin")

    assert calendar.status_code == 200
    assert events.status_code == 200
    assert events.json[0]["title"] == "Aula pública"
    assert admin.status_code == 302
    assert admin.headers["Location"].endswith("/login?next=/admin")


def test_student_can_login_and_logout_but_cannot_manage_events(system_client):
    login_response = login(system_client, "student.system@example.com")
    blocked = system_client.get("/admin", follow_redirects=True)
    logout_response = system_client.post("/logout", follow_redirects=True)

    assert login_response.status_code == 302
    assert blocked.status_code == 200
    assert b"Apenas l\xc3\xadderes e administradores" in blocked.data
    assert logout_response.status_code == 200
    with system_client.session_transaction() as session:
        assert not session


def test_leader_completes_create_view_edit_and_delete_flow(system_client):
    login(system_client, "leader.system@example.com")

    create = system_client.post("/admin/events/new", data=event_data())
    assert create.status_code == 302

    with system_client.application.app_context():
        event = Event.query.one()
        event_id = event.id
        assert event.classroom.name == "INFO4V"

    public_before_edit = system_client.get("/api/events")
    assert public_before_edit.json[0]["category"] == "Trabalho"

    edit = system_client.post(
        f"/admin/events/{event_id}/edit",
        data=event_data(
            title="Entrega revisada",
            category="Apresentação",
            end_at="2026-11-21T20:00",
        ),
    )
    assert edit.status_code == 302
    assert system_client.get("/api/events").json[0]["title"] == "Entrega revisada"

    delete = system_client.post(f"/admin/events/{event_id}/delete")
    assert delete.status_code == 302
    with system_client.application.app_context():
        assert db.session.get(Event, event_id) is None


def test_admin_role_can_manage_events_without_being_a_classroom_leader(system_client):
    login(system_client, "admin.system@example.com")

    response = system_client.post(
        "/admin/events/new",
        data=event_data(title="Evento administrativo", category="Evento"),
    )

    assert response.status_code == 302
    with system_client.application.app_context():
        assert Event.query.filter_by(title="Evento administrativo").count() == 1


def test_system_rejects_invalid_event_data_without_persisting(system_client):
    login(system_client, "leader.system@example.com")

    response = system_client.post(
        "/admin/events/new",
        data=event_data(
            title="",
            category="Categoria inexistente",
            start_at="2026-11-20T21:00",
            end_at="2026-11-20T19:00",
        ),
    )

    assert response.status_code == 422
    assert b"t\xc3\xadtulo" in response.data
    assert b"categoria v\xc3\xa1lida" in response.data
    assert "posterior ao início".encode() in response.data
    with system_client.application.app_context():
        assert Event.query.count() == 0


def test_registration_then_login_isolated_from_management_flow(tmp_path):
    database_path = tmp_path / "registration-system.sqlite"
    test_app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "registration-system-key",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path}",
        }
    )
    with test_app.app_context():
        db.session.add(Classroom(name="INFO4V", description="Turma ativa", active=True))
        db.session.commit()

    client = test_app.test_client()
    registration = client.post(
        "/register",
        data={
            "name": "Pessoa Integrante",
            "email": "integrante@example.com",
            "password": "senha-segura",
        },
    )
    login_response = client.post(
        "/login",
        data={"email": "integrante@example.com", "password": "senha-segura"},
    )

    assert registration.status_code == 302
    assert login_response.status_code == 302
    with test_app.app_context():
        user = User.query.filter_by(email="integrante@example.com").one()
        assert user.role == "student"
        assert user.password_hash != "senha-segura"
        db.drop_all()
