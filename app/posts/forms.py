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
from app import db
from app.users.models import User
from app.posts.models import utc_now
from wtforms import SelectMultipleField
from app.posts.models import Tag


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

    author_id = SelectField(
        "Автор",
        coerce=int,
        validators=[DataRequired(message="Оберіть автора.")],
    )

    tags = SelectMultipleField("Теги", coerce=int)
    
    submit = SubmitField("Зберегти")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        authors = db.session.scalars(
            db.select(User).order_by(User.id)
        ).all()
        self.author_id.choices = [
            (author.id, author.username) for author in authors
        ]

        tags = db.session.scalars(
            db.select(Tag).order_by(Tag.name)
        ).all()
        self.tags.choices = [
            (tag.id, tag.name) for tag in tags
        ]


class DeletePostForm(FlaskForm):
    submit = SubmitField("Видалити пост")