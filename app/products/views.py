from datetime import datetime
from pathlib import Path
from uuid import uuid4
from decimal import Decimal

from flask import (
    render_template, abort, redirect, url_for, flash, request
)

from app.products import products_bp
from app.products.forms import ProductForm, DeleteProductForm
from app.products.storage import products_table


@products_bp.route("")
@products_bp.route("/")
def product_list():
    with products_table() as table:
        products = []

        for document in table.all():
            product = dict(document)
            product["id"] = document.doc_id
            products.append(product)

    return render_template(
        "products/products.html",
        title="Товари",
        products=products
    )


@products_bp.route("/<int:product_id>")
def product_detail(product_id):
    with products_table() as table:
        document = table.get(doc_id=product_id)

    if document is None:
        abort(404)

    product = dict(document)
    product["id"] = document.doc_id

    return render_template(
        "products/detail_product.html",
        title=product["name"],
        product=product,
        delete_form=DeleteProductForm()
    )


@products_bp.route("/add", methods=["GET", "POST"])
def product_add():
    form = ProductForm()

    if form.validate_on_submit():
        image_path = ""

        if form.image.data:
            uploaded_file = form.image.data
            extension = Path(uploaded_file.filename).suffix.lower()
            filename = f"{uuid4().hex}{extension}"

            upload_folder = Path(products_bp.root_path) / "static" / "uploads"
            upload_folder.mkdir(parents=True, exist_ok=True)

            uploaded_file.save(upload_folder / filename)
            image_path = f"uploads/{filename}"

        product = {
            "name": form.name.data,
            "content": form.content.data,
            "price": format(form.price.data, ".2f"),
            "category": form.category.data,
            "quantity": form.quantity.data,
            "image": image_path,
            "created_at": datetime.now().isoformat(timespec="seconds")
        }

        with products_table() as table:
            product_id = table.insert(product)

        flash("Товар успішно додано.", "success")
        return redirect(
            url_for("products.product_detail", product_id=product_id)
        )

    if request.method == "POST":
        flash("Товар не додано. Перевірте поля форми.", "danger")

    return render_template(
        "products/product_form.html",
        title="Додати товар",
        form=form
    )

@products_bp.route("/<int:product_id>/edit", methods=["GET", "POST"])
def product_edit(product_id):
    with products_table() as table:
        document = table.get(doc_id=product_id)

    if document is None:
        abort(404)

    product = dict(document)

    form_data = dict(product)
    form_data["price"] = Decimal(product["price"])
    form_data.pop("image", None)

    form = ProductForm(data=form_data)

    if form.validate_on_submit():
        image_path = product.get("image", "")

        if form.image.data:
            uploaded_file = form.image.data
            extension = Path(uploaded_file.filename).suffix.lower()
            filename = f"{uuid4().hex}{extension}"

            upload_folder = Path(products_bp.root_path) / "static" / "uploads"
            upload_folder.mkdir(parents=True, exist_ok=True)

            uploaded_file.save(upload_folder / filename)
            image_path = f"uploads/{filename}"

        changes = {
            "name": form.name.data,
            "content": form.content.data,
            "price": format(form.price.data, ".2f"),
            "category": form.category.data,
            "quantity": form.quantity.data,
            "image": image_path
        }

        with products_table() as table:
            table.update(changes, doc_ids=[product_id])

        flash("Товар успішно оновлено.", "success")
        return redirect(
            url_for("products.product_detail", product_id=product_id)
        )

    if request.method == "POST":
        flash("Зміни не збережено. Перевірте поля форми.", "danger")

    return render_template(
        "products/product_form.html",
        title="Редагувати товар",
        form=form
    )


@products_bp.route("/<int:product_id>/delete", methods=["POST"])
def product_delete(product_id):
    form = DeleteProductForm()

    if not form.validate_on_submit():
        flash("Не вдалося підтвердити дію. Оновіть сторінку.", "danger")
        return redirect(
            url_for("products.product_detail", product_id=product_id)
        )

    with products_table() as table:
        if table.get(doc_id=product_id) is None:
            abort(404)

        table.remove(doc_ids=[product_id])

    flash("Товар видалено.", "success")
    return redirect(url_for("products.product_list"))