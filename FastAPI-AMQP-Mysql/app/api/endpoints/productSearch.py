import json
import aio_pika # type: ignore
from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.orm import Session
from app.connection.db import get_db
from app.services.product_service import fetch_product_search
from app.dtos.productsDto import PaginatedProductsResponse

router = APIRouter(prefix="/take", tags=["take"])

@router.get("/productsearch/{page}/{keyword}/", response_model=PaginatedProductsResponse)
async def productSearch(page: int = 1, 
                        keyword: str = None, 
                        request: Request = None,
                        db: Session = Depends(get_db)):
    products = await fetch_product_search(db=db, page=page, key=keyword)

    message_data = {
        "event": "product_search_viewed",
        "page": page,
        "count": len(products.items()),
        "user_id": getattr(request.state, "user_id", "anonymous")
    }

    message_body = json.dumps(message_data).encode()

    exchange = request.app.state.rmq_exchange    
    await exchange.publish(
        aio_pika.Message(body=message_body),
        routing_key="auth.productsearch.success"
    )

    return products