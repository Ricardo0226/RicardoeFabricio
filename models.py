from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class User:
    name: str
    email: str
    role: str = "student"
    id: int | None = None


@dataclass
class Classroom:
    name: str
    description: str = ""
    id: int | None = None


@dataclass
class Event:
    title: str
    start_at: datetime
    end_at: datetime
    classroom_id: int | None = None
    description: str = ""
    id: int | None = None
    metadata: dict[str, str] = field(default_factory=dict)
