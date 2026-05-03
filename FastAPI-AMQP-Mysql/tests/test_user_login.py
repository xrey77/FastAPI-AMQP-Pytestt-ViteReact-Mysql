import pytest # type: ignore
from httpx import ASGITransport, AsyncClient
from main import app
from app.connection.db import get_db
from unittest.mock import AsyncMock, MagicMock, ANY

@pytest.fixture
def mock_db_session():
    mock = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock
    yield mock
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_login_user_success(mocker, mock_db_session):
    
    # 1. Setup Mock Data
    mock_user = {"id": "123", "username": "Batman", "firstname": "Test User"}
    
    # Ensure the service returns the user as if validation passed
    mock_login = mocker.patch(
        "app.services.auth_service.user_account_login", 
        new_callable=AsyncMock, 
        return_value=mock_user
    )

    # Setup RMQ Mock
    mock_exchange = AsyncMock()
    app.state.rmq_exchange = mock_exchange

    # AsyncClient for async tests
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        login_data = {"username": "Batman", "password": "securepassword"}
        response = await ac.post("/auth/login/", json=login_data)


    # 5. Assertions
    assert response.status_code == 200
    assert response.json() == {"user": mock_user}
    
    # Verify the service was actually called with the data we sent    
    mock_login.assert_called_once_with(
        db=ANY, 
        username="Batman", 
        password="securepassword"
    )

    # Verify RMQ event
    mock_exchange.publish.assert_called_once()
    assert mock_exchange.publish.call_args.kwargs["routing_key"] == "auth.login.success"
