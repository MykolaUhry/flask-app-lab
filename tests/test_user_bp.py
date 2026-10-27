import unittest
from app import app


class UsersTestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_greetings_page(self):
        response = self.client.get("/users/hi/John?age=30")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"JOHN", response.data)
        self.assertIn(b"30", response.data)

    def test_admin_redirect(self):
        response = self.client.get("/users/admin")

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            "/users/hi/Administrator?age=45",
            response.headers["Location"]
        )

    def test_admin_page(self):
        response = self.client.get("/users/admin", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"ADMINISTRATOR", response.data)
        self.assertIn(b"45", response.data)


if __name__ == "__main__":
    unittest.main()