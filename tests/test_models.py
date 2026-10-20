from datetime import datetime

from models import Classroom, Event, User


def test_models_expose_relational_entities():
    assert User.__tablename__ == "users"
    assert Classroom.__tablename__ == "classrooms"
    assert Event.__tablename__ == "events"


def test_classroom_stores_basic_data():
    classroom = Classroom(name="INFO4V", description="Turma de informática")
    assert classroom.name == "INFO4V"
    assert classroom.description == "Turma de informática"


def test_event_links_to_a_classroom():
    start = datetime(2026, 10, 20, 19, 0)
    end = datetime(2026, 10, 20, 21, 0)
    event = Event(
        title="Aula de projeto",
        start_at=start,
        end_at=end,
        classroom_id=1,
    )

    assert event.classroom_id == 1
    assert event.has_valid_period()
