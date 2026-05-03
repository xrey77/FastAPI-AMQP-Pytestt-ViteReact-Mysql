import io
import pytest # type: ignore
from httpx import AsyncClient, ASGITransport
from main import app
from PIL import Image
from app.models.user import Users
from app.connection.db import get_db
from app.utils.jwtverification import get_current_user
from unittest.mock import AsyncMock, MagicMock
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
async def test_upload_profilepic_success(mocker, mock_db_session, mock_auth):

    user_data = {"sub": "123", "userid": "butch@jimenez.com"}
    token =  create_access_token(user_data)

    mock_user = Users(id="123", username="Butch")
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_user
    
    mock_db_session.execute.return_value = mock_result
    mocker.patch("app.api.endpoints.uploadProfilepic", return_value=mock_user)

    mock_exchange = AsyncMock()
    app.state.rmq_exchange = mock_exchange
    
    img = Image.new('RGB', (100, 100), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)

    files = {'userpic': ('test.jpg', img_byte_arr, 'image/jpeg')}
    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.patch("/api/uploadpicture/1/", files=files, headers=headers)

    assert response.status_code == 200
    assert response.json()["message"] == "Your profile photo has been successfully changed."
    
    mock_exchange.publish.assert_called_once()
    assert mock_exchange.publish.call_args.kwargs["routing_key"] == "auth.uploadpicture.success"
