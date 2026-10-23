from datetime import datetime

from app import create_app
from database import db
from models import Classroom, Event


def test_calendar_page_loads_fullcalendar():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )

    response = app.test_client().get("/")

    assert response.status_code == 200
    assert b"fullcalendar@6.1.15" in response.data
    assert b"id=\"calendar\"" in response.data


def test_events_endpoint_returns_calendar_format():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )

    with app.app_context():
        classroom = Classroom(name="INFO4V", description="Turma de informatica")
        event = Event(
            title="Aula de projeto",
            start_at=datetime(2026, 10, 20, 19, 0),
            end_at=datetime(2026, 10, 20, 21, 0),
            classroom=classroom,
            description="Revisao da sprint",
        )
        db.session.add(event)
        db.session.commit()

        response = app.test_client().get("/api/events")

    assert response.status_code == 200
    assert response.json == [
        {
            "id": event.id,
            "title": "Aula de projeto",
            "start": "2026-10-20T19:00:00",
            "end": "2026-10-20T21:00:00",
            "description": "Revisao da sprint",
            "classroom": "INFO4V",
        }
    ]
