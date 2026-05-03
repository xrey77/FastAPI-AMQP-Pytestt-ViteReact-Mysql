import pytest # type: ignore
from httpx import AsyncClient, ASGITransport
from main import app
from app.connection.db import get_db
from unittest.mock import AsyncMock, MagicMock

# Use a fixture to manage the override clean-up
@pytest.fixture
def mock_db_session():
    mock = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock
    yield mock
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_create_user_success(mocker, mock_db_session):

    # Setup Mocks
    mock_user = MagicMock(id=123)
    mocker.patch(
        "app.services.auth_service.create_user_account",
        new_callable=AsyncMock,
        return_value=mock_user
    )
    
    mock_exchange = AsyncMock()
    app.state.rmq_exchange = mock_exchange

    payload = {
        "firstname": "Butch", "lastname": "Jimenez",
        "email": "butch@jimenez.com", "mobile": "32423423",
        "username": "Butch", "password": "rey"
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/auth/register/", json=payload)

    # Success Assertions
    assert response.status_code == 201
    assert response.json()["message"] == "You have registered successfully."
    
    # RabbitMQ assertion
    mock_exchange.publish.assert_called_once()
    _, kwargs = mock_exchange.publish.call_args
    assert kwargs["routing_key"] == "auth.registration.success"
