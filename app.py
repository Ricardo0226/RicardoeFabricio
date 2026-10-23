import os

from flask import Flask, jsonify, render_template
from database import db


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "sprint-1-base-key"),
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            "DATABASE_URL", "sqlite:///classsync.db"
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    with app.app_context():
        import models  # noqa: F401

        db.create_all()

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api/events")
    def events():
        from models import Event

        calendar_events = [
            {
                "id": event.id,
                "title": event.title,
                "start": event.start_at.isoformat(),
                "end": event.end_at.isoformat(),
                "description": event.description,
                "classroom": event.classroom.name if event.classroom else None,
            }
            for event in Event.query.order_by(Event.start_at).all()
        ]
        return jsonify(calendar_events)

    return app


app = create_app()



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
