import os
import re

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from database import db

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_registration(name, email, password):
    errors = []
    if len(name) < 2 or len(name) > 120:
        errors.append("Informe um nome entre 2 e 120 caracteres.")
    if not EMAIL_PATTERN.fullmatch(email):
        errors.append("Informe um e-mail válido.")
    if len(password) < 8:
        errors.append("A senha deve ter pelo menos 8 caracteres.")
    return errors


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

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            name = (request.form.get("name") or "").strip()
            email = (request.form.get("email") or "").strip().lower()
            password = request.form.get("password") or ""
            errors = validate_registration(name, email, password)

            from models import Classroom, User

            if User.query.filter_by(email=email).first():
                errors.append("Este e-mail já está cadastrado.")
            classroom = Classroom.query.filter_by(active=True).order_by(Classroom.id).first()
            if classroom is None:
                errors.append("Não há turma ativa disponível para o cadastro.")

            if errors:
                for error in errors:
                    flash(error, "danger")
                return render_template("register.html"), 400

            user = User(name=name, email=email, role="student", classroom=classroom)
            user.set_password(password)
            db.session.add(user)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash("Este e-mail já está cadastrado.", "danger")
                return render_template("register.html"), 400

            flash("Cadastro realizado com sucesso. Você já pode acessar o sistema.", "success")
            return redirect(url_for("index"))

        return render_template("register.html")

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
