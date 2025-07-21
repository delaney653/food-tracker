"""Used to test different aspects of the Color website"""

import unittest
import os
import sys
import time
from sqlalchemy.exc import OperationalError

os.environ["ENV"] = "testing"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.app import app, db


class FlaskTests(unittest.TestCase):
    """Using unit tests to test different aspects of the Color website"""

    def setUp(self):
        """Sets up connection to testing database"""
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = (
            "mysql+pymysql://root:password@mysql-test/test_meals"
        )
        self.app = app.test_client()
        with app.app_context():
            for _ in range(10):
                try:
                    with db.engine.connect() as connection:
                        connection.execute(db.text("SELECT 1"))
                    break
                except OperationalError:
                    print("Test database not ready, retrying in 1s...")
                    time.sleep(2)
            else:
                raise OperationalError(
                    "Could not connect to test database after 5 tries"
                )

    def tearDown(self):
        # Cleans up database
        with app.app_context():
            with db.engine.connect() as connection:
                connection.execute(db.text("DELETE FROM meals"))
            db.session.commit()

    def test_home_page_data(self):
        """Testing if title loads correctly"""
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Meal Tracker", response.data)

    def test_e2e(self):
        """Simulating all features"""
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Meal Tracker", response.data)

        self.app.post("/add", data={"meal": "Chicken and potatoes", "rating": "Okay"})
        response = self.app.get("/")
        self.assertIn(b"Chicken and potatoes", response.data)
        self.assertIn(b"Okay", response.data)

        self.app.post("/delete/4")
        response = self.app.get("/")
        self.assertNotIn(b"Chicken and potatoes", response.data)
        self.assertNotIn(b": Okay", response.data)

        self.app.post(
            "/add", data={"meal": "fried macaroni bites", "rating": "DELICIOUS"}
        )
        response = self.app.get("/")
        self.assertIn(b"fried macaroni bites", response.data)
        self.assertIn(b"DELICIOUS", response.data)

        self.app.post(
            "/add", data={"meal": "Pesto tortellini", "rating": "Pretty Good"}
        )
        response = self.app.get("/")
        self.assertIn(b"Pesto tortellini", response.data)
        self.assertIn(b"Pretty Good", response.data)

        self.app.post(
            "/add",
            data={
                "meal": "Taco Bell bean and cheese burrito",
                "rating": "Didn't really like it",
            },
        )
        response = self.app.get("/")
        self.assertIn(b"Taco Bell bean and cheese burrito", response.data)
        self.assertIn(b"Didn&#39;t really like it", response.data)

        self.app.post(
            "/add", data={"meal": "Bartlett tuna casserole", "rating": "Nasty"}
        )
        response = self.app.get("/")
        self.assertIn(b"Bartlett tuna casserole", response.data)
        self.assertIn(b"Nasty", response.data)

        self.app.post("/delete/2")
        response = self.app.get("/")
        self.assertNotIn(b"Just mushrooms", response.data)
        self.assertNotIn(b"/delete/2", response.data)

        self.app.post("/delete/5")
        response = self.app.get("/")
        self.assertNotIn(b"fried macaroni bites", response.data)
        self.assertNotIn(b"/delete/5", response.data)


if __name__ == "__main__":
    unittest.main()
