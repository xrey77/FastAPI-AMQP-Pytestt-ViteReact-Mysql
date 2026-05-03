import pytest # type: ignore
from httpx import AsyncClient, ASGITransport
from main import app
from app.connection.db import get_db
from app.utils.jwtverification import get_current_user
from unittest.mock import AsyncMock, MagicMock
from app.utils.create_access_token import create_access_token
from types import SimpleNamespace

@pytest.fixture
def mock_db_session():
    mock = AsyncMock()
    app.dependency_overrides[get_db] = lambda: mock
    yield mock
    app.dependency_overrides.pop(get_db, None)

@pytest.fixture
def mock_auth():
    user_data = {"id": 123, "username": "Butch", "email": "butch@jimenez.com"}
    app.dependency_overrides[get_current_user] = lambda: user_data
    yield user_data
    app.dependency_overrides.pop(get_current_user, None)

@pytest.mark.asyncio
async def test_get_userid_success(mocker, mock_db_session, mock_auth):

    user_data = {"sub": "123", "userid": "butch@jimenez.com"}
    token =  create_access_token(user_data)

    mock_user_data = {
        "id": 123,
        "username": "Butch",
        "firstname": "Butch",
        "lastname": "Doe",
        "email": "butch@jimenez.com",
        "mobile": "123456789",
        "qrcodeurl": None,
        "userpic": "pix.png"
    }

    mock_user = SimpleNamespace(**mock_user_data)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_db_session.execute.return_value = mock_result

    mocker.patch("app.api.endpoints.getuserid.fetch_user_by_id", return_value=mock_user)

    mock_exchange = AsyncMock()
    app.state.rmq_exchange = mock_exchange

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/getuserid/123/", headers={"Authorization": "Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["firstname"] == "Butch"
    
    mock_exchange.publish.assert_called_once()
    assert mock_exchange.publish.call_args.kwargs["routing_key"] == "auth.getuserid.success"
