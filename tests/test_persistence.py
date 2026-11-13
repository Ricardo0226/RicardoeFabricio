from datetime import datetime
import sqlite3

import pytest

from app import create_app
from database import db
from models import Classroom, Event, User


@pytest.fixture()
def client(tmp_path):
    database_path = tmp_path / "test.sqlite"
    test_app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path}",
        }
    )
    with test_app.app_context():
        yield test_app.test_client()
        db.drop_all()


def test_user_is_persisted_with_student_role(client):
    with client.application.app_context():
        user = User(name="Ana", email="ana@example.com")
        db.session.add(user)
        db.session.commit()

        saved = db.session.get(User, user.id)
        assert saved is not None
        assert saved.role == "student"


def test_event_and_classroom_relationship_is_persisted(client):
    with client.application.app_context():
        classroom = Classroom(name="INFO4V", description="Turma de informática")
        event = Event(
            title="Aula de projeto",
            start_at=datetime(2026, 10, 20, 19, 0),
            end_at=datetime(2026, 10, 20, 21, 0),
            classroom=classroom,
        )
        db.session.add(event)
        db.session.commit()

        saved_event = db.session.get(Event, event.id)
        assert saved_event.classroom_id == classroom.id
        assert saved_event.classroom.name == "INFO4V"
        assert classroom.events[0].title == "Aula de projeto"


def test_existing_sqlite_database_receives_missing_event_category(tmp_path):
    database_path = tmp_path / "legacy.sqlite"
    connection = sqlite3.connect(database_path)
    connection.executescript(
        """
        CREATE TABLE events (
            id INTEGER PRIMARY KEY,
            title VARCHAR(160) NOT NULL,
            start_at DATETIME NOT NULL,
            end_at DATETIME NOT NULL,
            classroom_id INTEGER,
            description TEXT NOT NULL DEFAULT '',
            event_metadata JSON NOT NULL DEFAULT '{}'
        );
        INSERT INTO events
            (id, title, start_at, end_at, description, event_metadata)
        VALUES
            (1, 'Evento legado', '2026-11-10 19:00:00',
             '2026-11-10 20:00:00', 'Criado antes da categoria', '{}');
        """
    )
    connection.commit()
    connection.close()

    test_app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path}",
        }
    )

    with test_app.app_context():
        saved_event = db.session.get(Event, 1)
        assert saved_event is not None
        assert saved_event.category == "Evento"

        response = test_app.test_client().get("/api/events")
        assert response.status_code == 200
        assert response.json[0]["category"] == "Evento"
