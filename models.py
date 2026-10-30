from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from database import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(40), nullable=False, default="student")
    classroom_id = db.Column(db.Integer, db.ForeignKey("classrooms.id"), nullable=True)
    classroom = db.relationship("Classroom", back_populates="users")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return bool(self.password_hash) and check_password_hash(self.password_hash, password)


class Classroom(db.Model):
    __tablename__ = "classrooms"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    active = db.Column(db.Boolean, nullable=False, default=True)

    users = db.relationship("User", back_populates="classroom")
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
