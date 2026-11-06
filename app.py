import os
import re
from datetime import datetime
from functools import wraps

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database import db

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
ADMIN_ROLES = {"leader", "admin"}
EVENT_CATEGORIES = ("Prova", "Trabalho", "Apresentação", "Evento", "Outro")


def validate_registration(name, email, password):
    errors = []
    if len(name) < 2 or len(name) > 120:
        errors.append("Informe um nome entre 2 e 120 caracteres.")
    if not EMAIL_PATTERN.fullmatch(email):
        errors.append("Informe um e-mail válido.")
    if len(password) < 8:
        errors.append("A senha deve ter pelo menos 8 caracteres.")
    return errors


def parse_datetime(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def current_user():
    from models import User

    user_id = session.get("user_id")
    return db.session.get(User, user_id) if user_id else None


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if current_user() is None:
            flash("Faça login para continuar.", "warning")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if current_user().role not in ADMIN_ROLES:
            flash("Apenas líderes e administradores podem gerenciar compromissos.", "danger")
            return redirect(url_for("index"))
        return view(*args, **kwargs)

    return wrapped


def event_form_data(form):
    title = (form.get("title") or "").strip()
    description = (form.get("description") or "").strip()
    category = (form.get("category") or "").strip()
    start_at = parse_datetime(form.get("start_at"))
    end_at = parse_datetime(form.get("end_at"))
    errors = []
    if not title or len(title) > 160:
        errors.append("O título é obrigatório e deve ter até 160 caracteres.")
    if category not in EVENT_CATEGORIES:
        errors.append("Selecione uma categoria válida.")
    if not start_at:
        errors.append("Informe uma data e hora de início válidas.")
    if form.get("end_at") and not end_at:
        errors.append("Informe uma data e hora de término válida.")
    if start_at and end_at and end_at <= start_at:
        errors.append("O término deve ser posterior ao início.")
    return {
        "title": title,
        "description": description,
        "category": category,
        "start_at": start_at,
        "end_at": end_at or start_at,
    }, errors


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "sprint-1-base-key"),
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", "sqlite:///classsync.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    if test_config:
        app.config.update(test_config)
    db.init_app(app)
    with app.app_context():
        import models  # noqa: F401

        db.create_all()

    @app.context_processor
    def inject_user():
        user = current_user()
        return {"current_user": user, "is_admin": bool(user and user.role in ADMIN_ROLES)}

    @app.errorhandler(404)
    def not_found(error):
        return render_template(
            "error.html",
            code=404,
            message="A página ou compromisso solicitado não foi encontrado.",
        ), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        db.session.rollback()
        return render_template(
            "error.html",
            code=500,
            message="Ocorreu um erro inesperado. Tente novamente mais tarde.",
        ), 500

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

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = (request.form.get("email") or "").strip().lower()
            password = request.form.get("password") or ""
            from models import User

            user = User.query.filter_by(email=email).first()
            if user is None or not user.check_password(password):
                flash("E-mail ou senha inválidos.", "danger")
                return render_template("login.html"), 401
            session.clear()
            session["user_id"] = user.id
            session["user_name"] = user.name
            session["user_role"] = user.role
            flash("Login realizado com sucesso.", "success")
            return redirect(request.args.get("next") or url_for("index"))
        return render_template("login.html")

    @app.post("/logout")
    def logout():
        session.clear()
        flash("Logout realizado com sucesso.", "success")
        return redirect(url_for("index"))

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
                "category": event.category,
                "classroom": event.classroom.name if event.classroom else None,
            }
            for event in Event.query.order_by(Event.start_at).all()
        ]
        return jsonify(calendar_events)

    @app.get("/admin")
    @admin_required
    def admin():
        from models import Event

        events = Event.query.order_by(Event.start_at).all()
        return render_template("admin.html", events=events)

    @app.route("/admin/events/new", methods=["GET", "POST"])
    @admin_required
    def new_event():
        from models import Classroom, Event

        if request.method == "POST":
            data, errors = event_form_data(request.form)
            if errors:
                for error in errors:
                    flash(error, "danger")
                return render_template(
                    "event_form.html",
                    event=None,
                    form_title="Novo compromisso",
                    form_data=request.form,
                    categories=EVENT_CATEGORIES,
                ), 422
            user = current_user()
            classroom = user.classroom or Classroom.query.filter_by(active=True).order_by(Classroom.id).first()
            event = Event(**data, classroom=classroom)
            db.session.add(event)
            try:
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()
                return render_template("error.html", code=500, message="Não foi possível salvar o compromisso."), 500
            flash("Compromisso criado no calendário.", "success")
            return redirect(url_for("admin"))
        return render_template(
            "event_form.html",
            event=None,
            form_title="Novo compromisso",
            form_data={},
            categories=EVENT_CATEGORIES,
        )

    @app.route("/admin/events/<int:event_id>/edit", methods=["GET", "POST"])
    @admin_required
    def edit_event(event_id):
        from models import Event

        event = db.get_or_404(Event, event_id)
        if request.method == "POST":
            data, errors = event_form_data(request.form)
            if errors:
                for error in errors:
                    flash(error, "danger")
                return render_template(
                    "event_form.html",
                    event=event,
                    form_title="Editar compromisso",
                    form_data=request.form,
                    categories=EVENT_CATEGORIES,
                ), 422
            for key, value in data.items():
                setattr(event, key, value)
            try:
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()
                return render_template("error.html", code=500, message="Não foi possível atualizar o compromisso."), 500
            flash("Compromisso atualizado.", "success")
            return redirect(url_for("admin"))
        return render_template(
            "event_form.html",
            event=event,
            form_title="Editar compromisso",
            form_data={},
            categories=EVENT_CATEGORIES,
        )

    @app.post("/admin/events/<int:event_id>/delete")
    @admin_required
    def delete_event(event_id):
        from models import Event

        event = db.get_or_404(Event, event_id)
        db.session.delete(event)
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            return render_template("error.html", code=500, message="Não foi possível remover o compromisso."), 500
        flash("Compromisso removido.", "success")
        return redirect(url_for("admin"))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
