from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


class DashboardSmokeTest(unittest.TestCase):
    def test_dashboard_starts_without_exceptions(self):
        app = AppTest.from_file(str(ROOT / "dashboard" / "app.py"))
        app.run(timeout=30)

        self.assertEqual(len(app.exception), 0)


if __name__ == "__main__":
    unittest.main()
