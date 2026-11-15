import tempfile
import unittest
from pathlib import Path

from app import app
from app.products.storage import products_table


class ProductsTestCase(unittest.TestCase):
    def setUp(self):
        self.old_config = app.config.copy()
        self.temp_dir = tempfile.TemporaryDirectory()

        app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            PRODUCTS_DB_PATH=str(
                Path(self.temp_dir.name) / "products.json"
            ),
        )

        self.client = app.test_client()

    def tearDown(self):
        app.config.clear()
        app.config.update(self.old_config)
        self.temp_dir.cleanup()

    def product_data(self, **changes):
        data = {
            "name": "Тестовий ноутбук",
            "content": "Опис тестового товару",
            "price": "12500.50",
            "category": "laptop",
            "quantity": "3",
        }
        data.update(changes)
        return data

    def create_product(self):
        response = self.client.post(
            "/product/add",
            data=self.product_data(),
        )
        self.assertEqual(response.status_code, 302)

        with app.app_context():
            with products_table() as table:
                return table.all()[0].doc_id

    def read_product(self, product_id):
        with app.app_context():
            with products_table() as table:
                return table.get(doc_id=product_id)

    def test_products_list(self):
        self.create_product()

        response = self.client.get("/product")

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Тестовий ноутбук",
            response.get_data(as_text=True),
        )

    def test_product_creation(self):
        product_id = self.create_product()
        product = self.read_product(product_id)

        self.assertEqual(product["name"], "Тестовий ноутбук")
        self.assertEqual(product["price"], "12500.50")
        self.assertEqual(product["quantity"], 3)
        self.assertTrue(product["created_at"])

    def test_product_details(self):
        product_id = self.create_product()

        response = self.client.get(f"/product/{product_id}")

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Опис тестового товару",
            response.get_data(as_text=True),
        )

    def test_edit_page(self):
        product_id = self.create_product()

        response = self.client.get(f"/product/{product_id}/edit")

        self.assertEqual(response.status_code, 200)
        self.assertIn("12500.50", response.get_data(as_text=True))

    def test_product_editing(self):
        product_id = self.create_product()

        with app.app_context():
            with products_table() as table:
                table.update(
                    {"image": "uploads/old-photo.jpg"},
                    doc_ids=[product_id],
                )

        original = self.read_product(product_id)

        response = self.client.post(
            f"/product/{product_id}/edit",
            data=self.product_data(
                name="Оновлений ноутбук",
                price="9999.99",
                quantity="0",
            ),
        )

        self.assertEqual(response.status_code, 302)

        updated = self.read_product(product_id)
        self.assertEqual(updated["name"], "Оновлений ноутбук")
        self.assertEqual(updated["price"], "9999.99")
        self.assertEqual(updated["quantity"], 0)
        self.assertEqual(updated.doc_id, product_id)
        self.assertEqual(
            updated["created_at"], original["created_at"]
        )
        self.assertEqual(
            updated["image"], "uploads/old-photo.jpg"
        )

    def test_product_deletion(self):
        product_id = self.create_product()

        response = self.client.post(
            f"/product/{product_id}/delete"
        )

        self.assertEqual(response.status_code, 302)
        self.assertIsNone(self.read_product(product_id))

    def test_invalid_product(self):
        for changes in (
            {"name": "А"},
            {"price": "-10"},
            {"quantity": "-1"},
            {"category": "unknown"},
        ):
            with self.subTest(changes=changes):
                response = self.client.post(
                    "/product/add",
                    data=self.product_data(**changes),
                )
                self.assertEqual(response.status_code, 200)

                with app.app_context():
                    with products_table() as table:
                        self.assertEqual(len(table), 0)

    def test_missing_product(self):
        for url in (
            "/product/999999",
            "/product/999999/edit",
        ):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 404)

    def test_delete_requires_post(self):
        product_id = self.create_product()

        response = self.client.get(
            f"/product/{product_id}/delete"
        )

        self.assertEqual(response.status_code, 405)
        self.assertIsNotNone(self.read_product(product_id))

    def test_delete_without_csrf_token(self):
        product_id = self.create_product()
        app.config["WTF_CSRF_ENABLED"] = True

        self.client.post(f"/product/{product_id}/delete")

        self.assertIsNotNone(self.read_product(product_id))


if __name__ == "__main__":
    unittest.main()