import json
import aio_pika # type: ignore
from fastapi import APIRouter, Depends,Request
from sqlalchemy.orm import Session
from app.connection.db import get_db
from app.services.product_service import fetch_product_list
from app.dtos.productsDto import PaginatedProductsResponse

router = APIRouter(prefix="/take", tags=["take"])

@router.get("/productlist/{page}/", response_model=PaginatedProductsResponse)
async def productList(page: int = 1, 
                      request: Request = None,
                      db: Session = Depends(get_db)):
    
    products = await fetch_product_list(db=db, page=page)

    message_data = {
        "event": "product_list_viewed",
        "page": page,
        "count": len(products.items()),
        "user_id": getattr(request.state, "user_id", "anonymous")
    }

    message_body = json.dumps(message_data).encode()

    exchange = request.app.state.rmq_exchange    
    await exchange.publish(
        aio_pika.Message(body=message_body),
        routing_key="auth.productlist.success"
    )

    return products