import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture()
def client():
    original = app.user_middleware[0].kwargs["allow_remote"]
    app.user_middleware[0].kwargs["allow_remote"] = True
    app.middleware_stack = app.build_middleware_stack()
    try:
        with TestClient(app, base_url="http://127.0.0.1") as test_client:
            yield test_client
    finally:
        app.user_middleware[0].kwargs["allow_remote"] = original
        app.middleware_stack = app.build_middleware_stack()


def test_health_endpoint_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_primary_ui_routes_render_successfully(client):
    for path in ["/", "/expenses", "/review-queue", "/payroll", "/portfolio"]:
        response = client.get(path)

        assert response.status_code == 200
        assert "Household Engine" in response.text
