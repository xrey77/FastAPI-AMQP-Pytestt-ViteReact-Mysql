import pytest # type: ignore
from httpx import AsyncClient, ASGITransport
from main import app
from app.connection.db import get_db
from app.utils.jwtverification import get_current_user
from unittest.mock import AsyncMock, MagicMock, ANY
from app.utils.create_access_token import create_access_token

def override_get_current_user():
    return {"sub": "123", "userid": "butch@jimenez.com"}

app.dependency_overrides[get_current_user] = override_get_current_user

@pytest.fixture
def mock_db_session():
    mock = AsyncMock()
    app.dependency_overrides[get_db] = lambda: mock
    yield mock
    app.dependency_overrides.pop(get_db, None)

@pytest.fixture
def mock_auth():
    user_data = {"sub": 123, "username": "Butch", "email": "butch@jimenez.com"}
    app.dependency_overrides[override_get_current_user] = lambda: user_data
    yield user_data
    app.dependency_overrides.pop(get_current_user, None)

@pytest.mark.asyncio
async def test_mfa_activation_success(mocker, mock_db_session, mock_auth):

    user_data = {"sub": "123", "userid": "butch@jimenez.com"}
    token =  create_access_token(user_data)

    mock_user_data = {
        "message": "Multi-Factor Authenticator is enabled successfully."
    }

    mock_user = "Butch"
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_db_session.execute.return_value = mock_result

    mocker_activation = mocker.patch("app.api.endpoints.activateMfa.mfa_activate_totpd", return_value=mock_user)

    mock_exchange = AsyncMock()
    app.state.rmq_exchange = mock_exchange

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        activation_data = {"TwoFactorEnabled": True}
        response = await ac.patch("/api/activatemfa/1/", json=activation_data, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["message"] == "Multi-Factor Authenticator is enabled successfully."
    
    mock_exchange.publish.assert_called_once()
    assert mock_exchange.publish.call_args.kwargs["routing_key"] == "auth.mfaactivation.success"
