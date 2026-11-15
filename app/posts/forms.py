from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    BooleanField,
    DateTimeLocalField,
    SelectField,
    SubmitField,
)
from wtforms.validators import DataRequired, Length

from app.posts.models import utc_now


class PostForm(FlaskForm):
    title = StringField(
        "Заголовок",
        validators=[
            DataRequired(message="Введіть заголовок."),
            Length(
                max=150,
                message="Заголовок має містити не більше 150 символів.",
            ),
        ],
    )

    content = TextAreaField(
        "Текст поста",
        validators=[
            DataRequired(message="Введіть текст поста."),
        ],
    )

    enabled = BooleanField(
        "Показувати пост",
        default=True,
    )

    publish_date = DateTimeLocalField(
        "Дата публікації (UTC)",
        format="%Y-%m-%dT%H:%M",
        default=utc_now,
        validators=[
            DataRequired(message="Вкажіть дату й час публікації."),
        ],
    )

    category = SelectField(
        "Категорія",
        choices=[
            ("news", "Новини"),
            ("publication", "Публікація"),
            ("tech", "Технології"),
            ("other", "Інше"),
        ],
        default="other",
        validators=[
            DataRequired(message="Оберіть категорію."),
        ],
    )

    submit = SubmitField("Зберегти")


class DeletePostForm(FlaskForm):
    submit = SubmitField("Видалити пост")