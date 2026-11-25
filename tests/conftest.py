import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app  # noqa: E402


@pytest.fixture
def app():
    fd, path = tempfile.mkstemp(suffix=".sqlite")
    os.close(fd)
    os.unlink(path)
    app = create_app({"TESTING": True, "DATABASE": path, "SECRET_KEY": "test"})
    yield app
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def client(app):
    return app.test_client()
