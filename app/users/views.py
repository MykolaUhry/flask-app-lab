import re

from flask import (
    render_template, request, redirect, url_for,
    session, flash, make_response
)
from flask_login import (
    current_user, login_user, logout_user, login_required
)
from werkzeug.security import check_password_hash

from app import db, bcrypt
from app.users import users_bp
from app.users.models import User
from app.users.forms import RegistrationForm, LoginForm


@users_bp.route("/hi/<name>")
def greetings(name):
    age = request.args.get("age", "не вказано")
    return render_template(
        "users/hi.html",
        title="Привітання",
        name=name,
        age=age,
    )


@users_bp.route("/admin")
def admin():
    return redirect(
        url_for("users.greetings", name="Administrator", age=45)
    )


@users_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("users.account"))

    form = LoginForm()

    if form.validate_on_submit():
        user = db.session.scalar(
            db.select(User).where(
                User.username == form.username.data
            )
        )

        password_valid = False

        if user is not None:
            if user.password.startswith(("$2a$", "$2b$", "$2y$")):
                if len(form.password.data.encode("utf-8")) <= 72:
                    password_valid = bcrypt.check_password_hash(
                        user.password, form.password.data
                    )
            else:
                password_valid = check_password_hash(
                    user.password, form.password.data
                )

        if password_valid:
            session.clear()
            login_user(user)

            # Для сумісності з попередніми шаблонами.
            session["username"] = user.username
            session["email"] = user.email

            flash("Ви успішно увійшли!", "success")
            return redirect(url_for("users.account"))

        flash("Неправильне ім’я користувача або пароль.", "danger")

    return render_template(
        "users/login.html",
        title="Вхід",
        form=form,
    )


@users_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("users.account"))

    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=bcrypt.generate_password_hash(
                form.password.data
            ).decode("utf-8"),
        )

        db.session.add(user)
        db.session.commit()

        flash(
            "Реєстрація успішна! Тепер увійдіть у свій обліковий запис.",
            "success",
        )
        return redirect(url_for("users.login"))

    return render_template(
        "users/register.html",
        title="Реєстрація",
        form=form,
    )


@users_bp.route("/account")
@login_required
def account():
    return render_template(
        "users/account.html",
        title="Обліковий запис",
    )


@users_bp.route("/all")
@login_required
def users_list():
    users = db.session.scalars(
        db.select(User).order_by(User.id)
    ).all()

    return render_template(
        "users/users.html",
        title="Користувачі",
        users=users,
    )


@users_bp.route("/profile")
@login_required
def profile():
    cookies = {
        key[4:]: value
        for key, value in request.cookies.items()
        if key.startswith("lab_")
    }

    return render_template(
        "users/profile.html",
        title="Профіль",
        cookies=cookies,
    )


@users_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    session.pop("username", None)
    session.pop("email", None)

    flash("Ви вийшли з облікового запису.", "info")
    return redirect(url_for("users.login"))


@users_bp.route("/cookies/add", methods=["POST"])
@login_required
def add_cookie():
    key = request.form.get("key", "").strip()
    value = request.form.get("value", "").strip()
    days = request.form.get("days", type=int)

    if not re.fullmatch(r"[A-Za-z0-9_-]{1,50}", key):
        flash(
            "Ключ: від 1 до 50 символів — латинські літери, "
            "цифри, дефіс або підкреслення.",
            "danger",
        )
        return redirect(url_for("users.profile"))

    if not value or len(value.encode("utf-8")) > 500:
        flash("Введіть непорожнє коротке значення кукі.", "danger")
        return redirect(url_for("users.profile"))

    if days is None or not 1 <= days <= 365:
        flash("Термін дії має бути від 1 до 365 днів.", "danger")
        return redirect(url_for("users.profile"))

    flash(f"Кукі «{key}» збережено на {days} днів.", "success")
    response = make_response(redirect(url_for("users.profile")))
    response.set_cookie(
        f"lab_{key}",
        value,
        max_age=days * 24 * 60 * 60,
        httponly=True,
        samesite="Lax",
    )
    return response


@users_bp.route("/cookies/delete", methods=["POST"])
@login_required
def delete_cookie():
    key = request.form.get("key", "").strip()

    if f"lab_{key}" not in request.cookies:
        flash("Кукі з таким ключем не знайдено.", "warning")
        return redirect(url_for("users.profile"))

    flash(f"Кукі «{key}» видалено.", "success")
    response = make_response(redirect(url_for("users.profile")))
    response.delete_cookie(f"lab_{key}")
    return response


@users_bp.route("/cookies/delete-all", methods=["POST"])
@login_required
def delete_all_cookies():
    flash("Усі навчальні кукі видалено.", "success")
    response = make_response(redirect(url_for("users.profile")))

    for key in request.cookies:
        if key.startswith("lab_"):
            response.delete_cookie(key)

    return response


@users_bp.route("/theme", methods=["POST"])
@login_required
def change_theme():
    theme = request.form.get("theme")

    if theme not in ("light", "dark"):
        flash("Невідома тема.", "danger")
        return redirect(url_for("users.profile"))

    flash("Тему оформлення змінено.", "success")
    response = make_response(redirect(url_for("users.profile")))
    response.set_cookie(
        "theme",
        theme,
        max_age=365 * 24 * 60 * 60,
        httponly=True,
        samesite="Lax",
    )
    return response