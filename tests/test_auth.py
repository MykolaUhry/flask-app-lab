import unittest

from app import create_app, db, bcrypt
from app.users.models import User


class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.context = self.app.app_context()
        self.context.push()

        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def register(self, username="test_user", email="test@example.com"):
        return self.client.post(
            "/users/register",
            data={
                "username": username,
                "email": email,
                "password": "TestPassword789!",
                "confirm_password": "TestPassword789!",
            },
        )

    def login(self, password="TestPassword789!"):
        return self.client.post(
            "/users/login",
            data={
                "username": "test_user",
                "password": password,
            },
        )

    def test_registration_page(self):
        response = self.client.get("/users/register")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Реєстрація", response.get_data(as_text=True))

    def test_login_page(self):
        response = self.client.get("/users/login")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Увійти", response.get_data(as_text=True))

    def test_registration_saves_user_and_hash(self):
        response = self.register()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith("/users/login"))

        user = db.session.scalar(
            db.select(User).where(User.username == "test_user")
        )

        self.assertIsNotNone(user)
        self.assertEqual(user.email, "test@example.com")
        self.assertNotEqual(user.password, "TestPassword789!")
        self.assertTrue(
            bcrypt.check_password_hash(user.password, "TestPassword789!")
        )

    def test_duplicate_username(self):
        self.register()
        response = self.register(email="another@example.com")

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Таке ім’я користувача вже зайняте.",
            response.get_data(as_text=True),
        )
        self.assertEqual(
            db.session.scalar(db.select(db.func.count(User.id))),
            1,
        )

    def test_duplicate_email(self):
        self.register()
        response = self.register(username="another_user")

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Ця електронна пошта вже зареєстрована.",
            response.get_data(as_text=True),
        )
        self.assertEqual(
            db.session.scalar(db.select(db.func.count(User.id))),
            1,
        )

    def test_successful_login(self):
        self.register()
        response = self.login()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith("/users/account"))

        user = db.session.scalar(
            db.select(User).where(User.username == "test_user")
        )
        with self.client.session_transaction() as session:
            self.assertEqual(session["_user_id"], str(user.id))

        account = self.client.get("/users/account")
        self.assertEqual(account.status_code, 200)
        self.assertIn("test@example.com", account.get_data(as_text=True))

        users = self.client.get("/users/all")
        self.assertEqual(users.status_code, 200)
        self.assertIn("test_user", users.get_data(as_text=True))

    def test_wrong_password(self):
        self.register()
        response = self.login(password="WrongPassword")

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Неправильне ім’я користувача або пароль.",
            response.get_data(as_text=True),
        )
        with self.client.session_transaction() as session:
            self.assertNotIn("_user_id", session)

        self.assertEqual(
            self.client.get("/users/account").status_code,
            302,
        )

    def test_guest_cannot_access_protected_pages(self):
        for path in ("/users/account", "/users/all", "/users/profile"):
            with self.subTest(path=path):
                response = self.client.get(path)

                self.assertEqual(response.status_code, 302)
                self.assertIn(
                    "/users/login",
                    response.headers["Location"],
                )

    def test_logout(self):
        self.register()
        self.login()

        response = self.client.post("/users/logout")
        self.assertEqual(response.status_code, 302)

        with self.client.session_transaction() as session:
            self.assertNotIn("_user_id", session)
            self.assertNotIn("username", session)
            self.assertNotIn("email", session)

        for path in ("/users/account", "/users/all"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 302)
                self.assertIn("/users/login", response.headers["Location"])

    def test_authenticated_user_redirected_from_auth_pages(self):
        self.register()
        self.login()

        for path in ("/users/register", "/users/login"):
            with self.subTest(path=path):
                response = self.client.get(path)

                self.assertEqual(response.status_code, 302)
                self.assertTrue(
                    response.headers["Location"].endswith("/users/account")
                )


if __name__ == "__main__":
    unittest.main()