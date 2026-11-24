from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app import db
from typing import TYPE_CHECKING
from flask_login import UserMixin

if TYPE_CHECKING:
    from app.posts.models import Post


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False
    )
    password: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    posts: Mapped[list["Post"]] = relationship(
        "Post",
        back_populates="author"
    )

    def __repr__(self):
        return f"<User {self.id}: {self.username}>"