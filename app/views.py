import json
from datetime import datetime
from pathlib import Path

from flask import (
    current_app,
    render_template,
    redirect,
    url_for,
    flash,
    request,
)

from app.forms import ContactForm


def home():
    return render_template("homepage.html", title="Головна")


def resume():
    return render_template("resume.html", title="Резюме")


def contacts():
    form = ContactForm()

    if form.validate_on_submit():
        entry = {
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "name": form.name.data,
            "email": form.email.data,
            "subject": form.subject.data,
            "message": form.message.data,
        }

        log_path = (
            Path(current_app.root_path).parent
            / "logs"
            / "contacts.log"
        )

        try:
            log_path.parent.mkdir(parents=True, exist_ok=True)

            with log_path.open("a", encoding="utf-8") as log_file:
                log_file.write(
                    json.dumps(entry, ensure_ascii=False) + "\n"
                )

        except OSError:
            current_app.logger.exception(
                "Не вдалося записати контактне повідомлення."
            )
            flash(
                "Не вдалося зберегти повідомлення. Спробуйте пізніше.",
                "danger",
            )
        else:
            flash(
                "Повідомлення успішно прийнято та записано у файл.",
                "success",
            )

        return redirect(url_for("contacts"))

    if request.method == "POST":
        flash(
            "Форму не надіслано. Перевірте помилки нижче.",
            "danger",
        )

    return render_template(
        "contacts.html",
        title="Контакти",
        form=form,
    )


def register_views(app):
    app.add_url_rule("/", view_func=home)
    app.add_url_rule("/resume", view_func=resume)

    app.add_url_rule(
        "/contacts",
        view_func=contacts,
        methods=["GET", "POST"],
    )
    app.add_url_rule(
        "/contact",
        view_func=contacts,
        methods=["GET", "POST"],
    )