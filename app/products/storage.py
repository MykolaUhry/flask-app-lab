from contextlib import contextmanager
from pathlib import Path

from flask import current_app
from tinydb import TinyDB


@contextmanager
def products_table():
    default_path = (
        Path(current_app.root_path).parent / "data" / "products.json"
    )

    database_path = Path(
        current_app.config.get("PRODUCTS_DB_PATH", default_path)
    )

    database_path.parent.mkdir(parents=True, exist_ok=True)

    with TinyDB(
        str(database_path),
        encoding="utf-8",
        ensure_ascii=False,
        indent=4
    ) as database:
        yield database.table("products")