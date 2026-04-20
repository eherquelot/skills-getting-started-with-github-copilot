import copy
import unittest

from fastapi.testclient import TestClient

from src import app as app_module


class TestMergingtonApi(unittest.TestCase):
    def setUp(self):
        self.original_activities = copy.deepcopy(app_module.activities)
        self.client = TestClient(app_module.app)

    def tearDown(self):
        app_module.activities = self.original_activities

    def test_root_redirects_to_static_index(self):
        response = self.client.get("/", follow_redirects=False)

        self.assertEqual(response.status_code, 307)
        self.assertEqual(response.headers["location"], "/static/index.html")

    def test_get_activities_returns_expected_structure(self):
        response = self.client.get("/activities")

        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertIn("Chess Club", payload)
        self.assertIn("Programming Class", payload)
        self.assertIn("Gym Class", payload)

        for activity in payload.values():
            self.assertIn("description", activity)
            self.assertIn("schedule", activity)
            self.assertIn("max_participants", activity)
            self.assertIn("participants", activity)
            self.assertIsInstance(activity["participants"], list)

    def test_signup_for_existing_activity_adds_participant(self):
        email = "newstudent@mergington.edu"
        before_count = len(app_module.activities["Chess Club"]["participants"])

        response = self.client.post("/activities/Chess Club/signup", params={"email": email})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"message": f"Signed up {email} for Chess Club"},
        )
        self.assertEqual(
            len(app_module.activities["Chess Club"]["participants"]),
            before_count + 1,
        )
        self.assertIn(email, app_module.activities["Chess Club"]["participants"])

    def test_signup_for_unknown_activity_returns_not_found(self):
        response = self.client.post("/activities/Unknown/signup", params={"email": "student@mergington.edu"})

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Activity not found"})


if __name__ == "__main__":
    unittest.main()
