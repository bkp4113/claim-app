import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient


class TestHealthAPIModels(unittest.TestCase):
    def setUp(self):
        self.env_patcher = patch.dict(
            os.environ,
            {
                "DATABASE_URL": "sqlite:///:memory:",
                "ENVIRONMENT": "dev",
            },
        )

        self.env_patcher.start()
        from app.asgi import app

        self.app = TestClient(app=app)

    def teardown(self):
        pass

    @patch("app.__init__.initialize_psql_session")
    def test_get_health_200(self, mock_initialize_psql_session):
        response = self.app.get("/health")

        mock_initialize_psql_session.return_value = None

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "OK"})
