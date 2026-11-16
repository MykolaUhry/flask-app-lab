import unittest
from datetime import datetime

from app import create_app, db
from app.posts.models import Post


class PostsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()

        # Працюємо лише з окремою базою в пам'яті.
        self.assertEqual(
            self.app.config["SQLALCHEMY_DATABASE_URI"],
            "sqlite:///:memory:",
        )

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def create_post(self, title="Test post", is_active=True):
        with self.app.app_context():
            post = Post(
                title=title,
                content="Test content",
                category="tech",
                posted=datetime(2026, 11, 16, 12, 0),
                is_active=is_active,
                author="Mykola",
            )
            db.session.add(post)
            db.session.commit()
            return post.id

    def form_data(self):
        return {
            "title": "New post",
            "content": "New post content",
            "category": "tech",
            "publish_date": "2026-11-16T12:00",
            "enabled": "y",
        }

    def test_posts_list(self):
        self.create_post(title="Visible post")
        self.create_post(title="Hidden post", is_active=False)

        response = self.client.get("/post/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Visible post", response.data)
        self.assertNotIn(b"Hidden post", response.data)

    def test_post_details(self):
        post_id = self.create_post()

        response = self.client.get(f"/post/{post_id}")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Test post", response.data)
        self.assertIn(b"Test content", response.data)
        self.assertIn(b"Mykola", response.data)

    def test_missing_post(self):
        response = self.client.get("/post/99999")

        self.assertEqual(response.status_code, 404)

    def test_post_creation(self):
        response = self.client.post(
            "/post/create",
            data=self.form_data(),
        )

        self.assertEqual(response.status_code, 302)

        with self.app.app_context():
            post = db.session.scalar(
                db.select(Post).where(Post.title == "New post")
            )
            self.assertIsNotNone(post)
            self.assertEqual(post.content, "New post content")
            self.assertEqual(post.category, "tech")
            self.assertEqual(post.author, "Anonymous")
            self.assertTrue(post.is_active)
            self.assertEqual(
                post.posted,
                datetime(2026, 11, 16, 12, 0),
            )

    def test_invalid_post(self):
        data = self.form_data()
        data["title"] = ""

        response = self.client.post("/post/create", data=data)

        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            posts = db.session.scalars(db.select(Post)).all()
            self.assertEqual(len(posts), 0)

    def test_edit_page(self):
        post_id = self.create_post()

        response = self.client.get(f"/post/{post_id}/update")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Test post", response.data)
        self.assertIn(b"Test content", response.data)

    def test_post_editing(self):
        post_id = self.create_post()
        data = self.form_data()
        data["title"] = "Updated post"
        data.pop("enabled")

        response = self.client.post(
            f"/post/{post_id}/update",
            data=data,
        )

        self.assertEqual(response.status_code, 302)

        with self.app.app_context():
            post = db.session.get(Post, post_id)
            self.assertEqual(post.title, "Updated post")
            self.assertEqual(post.content, "New post content")
            self.assertEqual(post.author, "Mykola")
            self.assertFalse(post.is_active)

    def test_delete_confirmation(self):
        post_id = self.create_post()

        response = self.client.get(f"/post/{post_id}/delete")

        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            self.assertIsNotNone(db.session.get(Post, post_id))

    def test_post_deletion(self):
        post_id = self.create_post()

        response = self.client.post(f"/post/{post_id}/delete")

        self.assertEqual(response.status_code, 302)

        with self.app.app_context():
            self.assertIsNone(db.session.get(Post, post_id))

    def test_delete_without_csrf_token(self):
        post_id = self.create_post()
        self.app.config["WTF_CSRF_ENABLED"] = True

        self.client.post(f"/post/{post_id}/delete")

        with self.app.app_context():
            self.assertIsNotNone(db.session.get(Post, post_id))


if __name__ == "__main__":
    unittest.main()