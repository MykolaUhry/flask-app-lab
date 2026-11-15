from flask import Blueprint

products_bp = Blueprint(
    "products",
    __name__,
    template_folder="templates",
    static_folder="static",
    url_prefix="/product"
)

from app.products import views