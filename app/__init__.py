import os
from pathlib import Path
from sqlalchemy import MetaData
from flask import Flask, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from app.config import configurations
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    })


db = SQLAlchemy(model_class=Base)
migrate = Migrate()
bcrypt = Bcrypt()

login_manager = LoginManager()
login_manager.login_view = "users.login"
login_manager.login_message = "Спочатку увійдіть у свій обліковий запис."
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    from app.users.models import User

    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv("APP_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(configurations[config_name])

    if not app.config["SECRET_KEY"]:
        raise RuntimeError("Додайте SECRET_KEY у файл .env")

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from app.views import register_views
    from app.users import users_bp
    from app.products import products_bp
    from app.posts import post_bp

    register_views(app)
    app.register_blueprint(users_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(post_bp)

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template(
            "404.html",
            title="Сторінку не знайдено",
        ), 404

    return app