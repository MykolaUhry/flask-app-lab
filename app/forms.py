from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class ContactForm(FlaskForm):
    name = StringField(
        "Ваше ім’я",
        validators=[
            DataRequired(message="Введіть ім’я."),
            Length(
                min=2,
                max=50,
                message="Ім’я має містити від 2 до 50 символів."
            )
        ]
    )

    email = StringField(
        "Електронна пошта",
        validators=[
            DataRequired(message="Введіть електронну пошту."),
            Email(message="Введіть коректну адресу електронної пошти."),
            Length(max=120, message="Адреса має містити до 120 символів.")
        ]
    )

    subject = SelectField(
        "Тема звернення",
        choices=[
            ("", "Оберіть тему"),
            ("question", "Запитання"),
            ("cooperation", "Співпраця"),
            ("feedback", "Відгук")
        ],
        validators=[
            DataRequired(message="Оберіть тему звернення.")
        ]
    )

    message = TextAreaField(
        "Повідомлення",
        validators=[
            DataRequired(message="Введіть повідомлення."),
            Length(
                min=10,
                max=2000,
                message="Повідомлення має містити від 10 до 2000 символів."
            )
        ]
    )

    submit = SubmitField("Надіслати")