import pytest # type: ignore
from httpx import AsyncClient, ASGITransport
from main import app
from app.connection.db import get_db
from app.utils.jwtverification import get_current_user
from unittest.mock import AsyncMock, MagicMock
from app.utils.create_access_token import create_access_token
from types import SimpleNamespace

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
async def test_get_users_success(mocker, mock_db_session, mock_auth):

    user_data = {"sub": "123", "userid": "butch@jimenez.com"}
    token =  create_access_token(user_data)

    mock_user_data = {
        "page": 1,
        "totpage": 1,
        "totalrecords": 4,
        "users": [
            {
                "id": 1,
                "firstname": "Butch",
                "lastname": "Gragasin",
                "username": "Butch",
                "email": "bucth@jimenez.com",
                "mobile": "+5334343",
                "userpic": "001.JPEG",
                "role_id": 1,
                "department_id": 1,
                "isactivated": 1,
                "isblocked": 0,
                "created_at": "2026-05-01T07:15:03",
                "updated_at": "2026-05-02T10:49:58"
            },
        ]
    }

    mock_user = SimpleNamespace(**mock_user_data)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_db_session.execute.return_value = mock_result

    mocker.patch("app.api.endpoints.getusers.fetch_all_users", return_value=mock_user)

    mock_exchange = AsyncMock()
    app.state.rmq_exchange = mock_exchange

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/getusers/1/", headers={"Authorization": "Bearer {token}"})

    assert response.status_code == 200
    assert response.json() == mock_user_data
    
    mock_exchange.publish.assert_called_once()
    args, kwargs = app.state.rmq_exchange.publish.call_args
    message = args[0]
    assert b"get_all_users" in message.body
    assert mock_exchange.publish.call_args.kwargs["routing_key"] == "auth.getallusers.success"

    # assert kwargs["routing_key"] == "auth.getallusers.success"