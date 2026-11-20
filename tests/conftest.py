"""Shared test setup (pytest 'fixtures'). Every test gets a FRESH app,
so one test changing stock never affects another test."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))   # lets tests import "shopkart"

from shopkart import create_app  # noqa: E402


@pytest.fixture
def app():
    return create_app(env="development")


@pytest.fixture
def client(app):
    return app.test_client()       # fake browser - no server needed


@pytest.fixture
def valid_order():
    return {
        "customer_email": "priya@example.com",
        "address": {"name": "Priya Sharma", "city": "Bengaluru",
                    "pincode": "560001", "phone": "9876543210"},
        "items": [{"product_id": 101, "quantity": 2}],
    }
