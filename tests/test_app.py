import copy
import unittest

from fastapi import HTTPException

from src import app as app_module


class TestActivitiesApp(unittest.TestCase):
    def setUp(self):
        self.original_activities = copy.deepcopy(app_module.activities)

    def tearDown(self):
        app_module.activities = self.original_activities

    def test_root_redirects_to_static_index(self):
        response = app_module.root()

        self.assertEqual(response.status_code, 307)
        self.assertEqual(response.headers["location"], "/static/index.html")

    def test_get_activities_returns_expected_structure(self):
        payload = app_module.get_activities()

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

        result = app_module.signup_for_activity("Chess Club", email)

        self.assertEqual(result, {"message": f"Signed up {email} for Chess Club"})
        self.assertEqual(
            len(app_module.activities["Chess Club"]["participants"]),
            before_count + 1,
        )
        self.assertIn(email, app_module.activities["Chess Club"]["participants"])

    def test_signup_for_unknown_activity_raises_not_found(self):
        with self.assertRaises(HTTPException) as context:
            app_module.signup_for_activity("Unknown", "student@mergington.edu")

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Activity not found")


if __name__ == "__main__":
    unittest.main()
