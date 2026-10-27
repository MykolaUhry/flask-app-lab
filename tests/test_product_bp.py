import unittest
from app import app


class ProductsTestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_products_list(self):
        response = self.client.get("/products/")

        self.assertEqual(response.status_code, 200)

        for name in ("Laptop", "Phone", "PC"):
            self.assertIn(name, response.get_data(as_text=True))

    def test_product_details(self):
        cases = [
            (1, "Laptop", "1200", "Intel Core i7"),
            (2, "Phone", "800", "OLED"),
            (3, "PC", "1800", "RTX 4070"),
        ]

        for product_id, name, price, description in cases:
            with self.subTest(product_id=product_id):
                response = self.client.get(f"/products/{product_id}")
                html = response.get_data(as_text=True)

                self.assertEqual(response.status_code, 200)
                self.assertIn(name, html)
                self.assertIn(price, html)
                self.assertIn(description, html)

    def test_missing_product(self):
        response = self.client.get("/products/999")

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()