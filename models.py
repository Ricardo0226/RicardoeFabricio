from datetime import datetime

from database import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    role = db.Column(db.String(40), nullable=False, default="student")


class Classroom(db.Model):
    __tablename__ = "classrooms"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")

    events = db.relationship(
        "Event",
        back_populates="classroom",
        cascade="all, delete-orphan",
    )


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    start_at = db.Column(db.DateTime, nullable=False)
    end_at = db.Column(db.DateTime, nullable=False)
    classroom_id = db.Column(
        db.Integer,
        db.ForeignKey("classrooms.id"),
        nullable=True,
    )
    description = db.Column(db.Text, nullable=False, default="")
    event_metadata = db.Column(db.JSON, nullable=False, default=dict)

    classroom = db.relationship("Classroom", back_populates="events")

    def has_valid_period(self) -> bool:
        return isinstance(self.start_at, datetime) and self.start_at < self.end_at
