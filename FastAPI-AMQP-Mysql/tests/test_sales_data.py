import pytest # type: ignore
from httpx import AsyncClient, ASGITransport
from main import app
from app.models.product import Products
from app.connection.db import get_db
from unittest.mock import AsyncMock, MagicMock
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal

@pytest.fixture
def mock_db_session():
    mock = AsyncMock()
    app.dependency_overrides[get_db] = lambda: mock
    yield mock
    app.dependency_overrides.pop(get_db, None)

@pytest.mark.asyncio
async def test_sales_data_success(mocker):

    # 1. Mock the Database result
    mock_sales_data = {
    "sales": [
        {
            "id": 1,
            "salesamount": Decimal("10.00"),
            "salesdate": "2025-01-30T13:14:04"
        }
    ]
    }
    
    # Mock the internal fetch function
    mocker.patch("app.api.endpoints.saleData", 
                 new_callable=AsyncMock, 
                 return_value=mock_sales_data)

    # 2. Mock RabbitMQ (app.state.rmq_exchange)
    mock_exchange = AsyncMock()
    app.state.rmq_exchange = mock_exchange

    # 3. Execute request
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/take/salesdata/")

    # 4. Assertions
    assert response.status_code == 200
 
    
    # Verify RabbitMQ was called
    mock_exchange.publish.assert_called_once()
    assert mock_exchange.publish.call_args.kwargs["routing_key"] == "auth.salesdata.success"