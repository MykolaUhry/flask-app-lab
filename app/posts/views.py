from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    session,
)

from app import db
from app.posts import post_bp
from app.posts.forms import PostForm, DeletePostForm
from app.posts.models import Post


@post_bp.route("")
@post_bp.route("/")
def post_list():
    posts = db.session.scalars(
        db.select(Post)
        .where(Post.is_active.is_(True))
        .order_by(Post.posted.desc())
    ).all()

    return render_template(
        "posts/all_posts.html",
        title="Пости",
        posts=posts,
    )


@post_bp.route("/<int:post_id>")
def post_detail(post_id):
    post = db.get_or_404(Post, post_id)

    return render_template(
        "posts/detail_post.html",
        title=post.title,
        post=post,
    )


@post_bp.route("/create", methods=["GET", "POST"])
def post_create():
    form = PostForm()

    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            category=form.category.data,
            posted=form.publish_date.data,
            is_active=form.enabled.data,
            author=session.get("username") or "Anonymous",
        )

        db.session.add(post)
        db.session.commit()

        flash("Пост успішно створено.", "success")
        return redirect(
            url_for("posts.post_detail", post_id=post.id)
        )

    return render_template(
        "posts/add_post.html",
        title="Створення поста",
        form=form,
    )


@post_bp.route("/<int:post_id>/update", methods=["GET", "POST"])
def post_update(post_id):
    post = db.get_or_404(Post, post_id)
    form = PostForm()

    if request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
        form.category.data = post.category
        form.publish_date.data = post.posted
        form.enabled.data = post.is_active

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.category = form.category.data
        post.posted = form.publish_date.data
        post.is_active = form.enabled.data

        db.session.commit()

        flash("Пост успішно оновлено.", "success")
        return redirect(
            url_for("posts.post_detail", post_id=post.id)
        )

    return render_template(
        "posts/add_post.html",
        title="Редагування поста",
        form=form,
    )


@post_bp.route("/<int:post_id>/delete", methods=["GET", "POST"])
def post_delete(post_id):
    post = db.get_or_404(Post, post_id)
    form = DeletePostForm()

    if form.validate_on_submit():
        db.session.delete(post)
        db.session.commit()

        flash("Пост видалено.", "success")
        return redirect(url_for("posts.post_list"))

    if request.method == "POST":
        flash(
            "Не вдалося підтвердити видалення. Спробуйте ще раз.",
            "danger",
        )

    return render_template(
        "posts/delete_confirm.html",
        title="Видалення поста",
        post=post,
        form=form,
    )