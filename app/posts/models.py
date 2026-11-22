from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, DateTime, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app import db
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.users.models import User


post_tags = db.Table(
    "post_tags",
    db.Column(
        "post_id",
        db.Integer,
        db.ForeignKey("post.id"),
        primary_key=True,
    ),
    db.Column(
        "tag_id",
        db.Integer,
        db.ForeignKey("tags.id"),
        primary_key=True,
    ),
)

def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Post(db.Model):
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    posted: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        Enum(
            "news",
            "publication",
            "tech",
            "other",
            name="post_category",
            create_constraint=True,
            validate_strings=True,
        ),
        default="other",
        nullable=False,
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="1",
        nullable=False,
    )

    author_id: Mapped[int | None] = mapped_column(
        db.ForeignKey("users.id"),
        nullable=True
    )

    author: Mapped["User | None"] = relationship(
        "User",
        back_populates="posts"
    )

    tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        secondary=post_tags,
        back_populates="posts",
    )

    def __repr__(self):
        return f"<Post id={self.id} title={self.title!r}>"

class Tag(db.Model):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    posts: Mapped[list["Post"]] = relationship(
        "Post",
        secondary=post_tags,
        back_populates="tags",
    )

    def __repr__(self):
        return f"<Tag {self.name}>"