from decimal import Decimal

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileSize
from wtforms import (
    StringField,
    TextAreaField,
    DecimalField,
    SelectField,
    IntegerField,
    SubmitField
)
from wtforms.validators import (
    DataRequired,
    InputRequired,
    Length,
    NumberRange,
    ValidationError
)


class ProductForm(FlaskForm):
    name = StringField(
        "Назва товару",
        validators=[
            DataRequired(message="Введіть назву товару."),
            Length(
                min=3,
                max=100,
                message="Назва має містити від 3 до 100 символів."
            )
        ]
    )

    content = TextAreaField(
        "Опис товару",
        validators=[
            DataRequired(message="Введіть опис товару."),
            Length(max=5000, message="Опис має містити до 5000 символів.")
        ],
        render_kw={"rows": 5, "cols": 40}
    )

    price = DecimalField(
        "Ціна",
        places=2,
        validators=[
            InputRequired(message="Введіть ціну.")
        ],
        render_kw={"min": "0.01", "step": "0.01"}
    )

    category = SelectField(
        "Категорія",
        choices=[
            ("", "Оберіть категорію"),
            ("laptop", "Ноутбуки"),
            ("phone", "Телефони"),
            ("pc", "Комп’ютери"),
            ("accessory", "Аксесуари")
        ],
        validators=[
            DataRequired(message="Оберіть категорію.")
        ]
    )

    quantity = IntegerField(
        "Кількість",
        validators=[
            InputRequired(message="Введіть кількість."),
            NumberRange(
                min=0,
                message="Кількість має бути невід’ємним цілим числом."
            )
        ],
        render_kw={"min": "0", "step": "1"}
    )

    image = FileField(
        "Зображення товару",
        validators=[
            FileAllowed(
                ["png", "jpg", "jpeg"],
                message="Дозволені лише PNG, JPG та JPEG."
            ),
            FileSize(
                max_size=2 * 1024 * 1024,
                message="Розмір зображення має бути не більше 2 МБ."
            )
        ]
    )

    submit = SubmitField("Зберегти товар")

    def validate_price(self, field):
        price = field.data

        if price is None or not price.is_finite():
            raise ValidationError("Введіть коректну ціну.")

        if price < Decimal("0.01"):
            raise ValidationError("Ціна має бути не меншою за 0.01.")

        if price != price.quantize(Decimal("0.01")):
            raise ValidationError("Ціна може мати не більше двох знаків після коми.")


class DeleteProductForm(FlaskForm):
    submit = SubmitField("Видалити товар")