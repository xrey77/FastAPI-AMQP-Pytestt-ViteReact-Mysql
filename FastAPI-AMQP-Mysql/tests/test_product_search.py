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
async def test_product_list_success(mocker):

    # 1. Mock the Database result
    mock_products_data = {
        "page": 1,
        "totpage": 4,
        "totalrecords": 16,
        "products": [
            {
                "id": 1,
                "descriptions": "CINEO X100 SERIES",
                "qty": 10,
                "unit": "pcs",
                "costprice": Decimal("10.00"),
                "sellprice": Decimal("15.00"),
                "saleprice": Decimal("12.00"),
                "productpicture": "test.jpg",
                "alertstocks": 5,
                "criticalstocks": 2
            }
        ]
    }
    
    # Mock the internal fetch function
    mocker.patch("app.api.endpoints.productSearch", 
                 new_callable=AsyncMock, 
                 return_value=mock_products_data)

    # 2. Mock RabbitMQ (app.state.rmq_exchange)
    mock_exchange = AsyncMock()
    app.state.rmq_exchange = mock_exchange

    # 3. Execute request
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/take/productsearch/1/cineo/")

    # 4. Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["totalrecords"] == 16
    assert data["totpage"] == 4
    assert data["page"] == 1
 
    
    # Verify RabbitMQ was called
    mock_exchange.publish.assert_called_once()
    assert mock_exchange.publish.call_args.kwargs["routing_key"] == "auth.productsearch.success"