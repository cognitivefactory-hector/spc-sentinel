"""M0 smoke test: the scaffold serves the dashboard page with its disclaimer.

Real SPC-engine tests (TDD, per PLAN.md) arrive in M1 under tests/test_rules.py etc.
"""

import pytest
from django.test import Client


@pytest.fixture
def client():
    return Client()


def test_index_serves_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"SPC Sentinel" in response.content


def test_index_has_synthetic_data_disclaimer(client):
    # SPEC.md §8 requires the disclaimer in the UI footer.
    response = client.get("/")
    assert b"not affiliated with any employer" in response.content
