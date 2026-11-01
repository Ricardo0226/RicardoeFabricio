from datetime import datetime

import pytest

from app import create_app
from database import db
from models import Classroom, Event, User


@pytest.fixture()
def client(tmp_path):
    database_path = tmp_path / "events.sqlite"
    test_app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-key",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path}",
        }
    )
    with test_app.app_context():
        classroom = Classroom(name="INFO4V", description="Turma ativa", active=True)
        leader = User(
            name="Líder",
            email="lider@example.com",
            role="leader",
            classroom=classroom,
        )
        leader.set_password("senha-segura")
        student = User(
            name="Estudante",
            email="aluno@example.com",
            role="student",
            classroom=classroom,
        )
        student.set_password("senha-segura")
        db.session.add_all([classroom, leader, student])
        db.session.commit()
        yield test_app.test_client()
        db.drop_all()


def login(client, email):
    return client.post(
        "/login",
        data={"email": email, "password": "senha-segura"},
    )


def test_event_management_requires_leader_or_admin(client):
    assert client.get("/admin").status_code == 302
    login(client, "aluno@example.com")
    response = client.get("/admin")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_leader_can_create_edit_and_delete_event(client):
    login(client, "lider@example.com")

    create = client.post(
        "/admin/events/new",
        data={
            "title": "Reunião de projeto",
            "description": "Apresentação da sprint",
            "start_at": "2026-11-10T19:00",
            "end_at": "2026-11-10T21:00",
        },
    )
    assert create.status_code == 302

    with client.application.app_context():
        event = Event.query.one()
        event_id = event.id
        assert event.title == "Reunião de projeto"
        assert event.classroom.name == "INFO4V"

    edit = client.post(
        f"/admin/events/{event_id}/edit",
        data={
            "title": "Reunião atualizada",
            "description": "Pauta revisada",
            "start_at": "2026-11-11T19:00",
            "end_at": "2026-11-11T20:00",
        },
    )
    assert edit.status_code == 302

    with client.application.app_context():
        saved = db.session.get(Event, event_id)
        assert saved.title == "Reunião atualizada"
        assert saved.start_at == datetime(2026, 11, 11, 19, 0)

    public_events = client.get("/api/events")
    assert public_events.status_code == 200
    assert public_events.json[0]["title"] == "Reunião atualizada"

    delete = client.post(f"/admin/events/{event_id}/delete")
    assert delete.status_code == 302
    with client.application.app_context():
        assert db.session.get(Event, event_id) is None


def test_event_creation_rejects_invalid_period(client):
    login(client, "lider@example.com")
    response = client.post(
        "/admin/events/new",
        data={
            "title": "Período inválido",
            "start_at": "2026-11-10T21:00",
            "end_at": "2026-11-10T19:00",
        },
    )
    assert response.status_code == 422
    assert b"posterior ao in\xc3\xADcio" in response.data
    with client.application.app_context():
        assert Event.query.count() == 0


def test_missing_event_returns_not_found_for_leader(client):
    login(client, "lider@example.com")
    assert client.get("/admin/events/999999/edit").status_code == 404
