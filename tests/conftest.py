import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-test-key")

from app import app as flask_app

@pytest.fixture
def app():
    flask_app.config["TESTING"] = True
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()
