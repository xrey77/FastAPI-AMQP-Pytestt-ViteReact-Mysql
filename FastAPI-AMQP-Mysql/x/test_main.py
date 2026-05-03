import pytest # type: ignore
from fastapi.testclient import TestClient
from main import app
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from app.connection.db import get_db

client = TestClient(app)

# 1. Mock the Database session
mock_db = MagicMock()

# 2. Override the get_db dependency
def override_get_db():
    yield mock_db

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.mark.asyncio
async def test_login_user_success(mocker):
    # Mock the auth_service
    mock_user = {"id": "123", "username": "Batman", "password": "robin", "firstname": "Test User"}
    mocker.patch(
        "app.services.auth_service.user_account_login", 
        new_callable=AsyncMock, 
        return_value=mock_user
    )

    # Mock the RabbitMQ exchange on the app state
    mock_exchange = AsyncMock()
    app.state.rmq_exchange = mock_exchange

    login_data = {"username": "Batman", "password": "securepassword"}

    # Call the endpoint
    response = client.post("/auth/login/", json=login_data)

    # Assert: Status and Response body
    assert response.status_code == 200
    assert response.json() == {"user": mock_user}

    # Assert: Verify RabbitMQ message was "sent"
    mock_exchange.publish.assert_called_once()
    args, kwargs = mock_exchange.publish.call_args
    assert kwargs["routing_key"] == "auth.login.success"
