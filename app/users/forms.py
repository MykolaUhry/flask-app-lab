from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, ValidationError
)

from app import db
from app.users.models import User


class RegistrationForm(FlaskForm):
    username = StringField(
        "Ім’я користувача",
        validators=[
            DataRequired(message="Введіть ім’я користувача."),
            Length(min=3, max=100, message="Від 3 до 100 символів."),
        ],
        filters=[lambda value: value.strip() if value else value],
    )

    email = StringField(
        "Електронна пошта",
        validators=[
            DataRequired(message="Введіть електронну пошту."),
            Email(message="Введіть коректну електронну пошту."),
            Length(max=120, message="Не більше 120 символів."),
        ],
        filters=[lambda value: value.strip().lower() if value else value],
    )

    password = PasswordField(
        "Пароль",
        validators=[
            DataRequired(message="Введіть пароль."),
            Length(min=8, message="Пароль має містити щонайменше 8 символів."),
        ],
    )

    confirm_password = PasswordField(
        "Повторіть пароль",
        validators=[
            DataRequired(message="Повторіть пароль."),
            EqualTo("password", message="Паролі не збігаються."),
        ],
    )

    submit = SubmitField("Зареєструватися")

    def validate_username(self, field):
        user = db.session.scalar(
            db.select(User).where(User.username == field.data)
        )
        if user is not None:
            raise ValidationError("Таке ім’я користувача вже зайняте.")

    def validate_email(self, field):
        user = db.session.scalar(
            db.select(User).where(User.email == field.data)
        )
        if user is not None:
            raise ValidationError("Ця електронна пошта вже зареєстрована.")

    def validate_password(self, field):
        if len(field.data.encode("utf-8")) > 72:
            raise ValidationError(
                "Пароль має займати не більше 72 байтів у UTF-8."
            )

class LoginForm(FlaskForm):
    username = StringField(
        "Ім’я користувача",
        validators=[
            DataRequired(message="Введіть ім’я користувача."),
            Length(max=100, message="Не більше 100 символів."),
        ],
        filters=[lambda value: value.strip() if value else value],
    )

    password = PasswordField(
        "Пароль",
        validators=[
            DataRequired(message="Введіть пароль."),
        ],
    )

    submit = SubmitField("Увійти")