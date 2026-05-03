import json
import aio_pika # type: ignore
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.connection.db import get_db
from app.services.product_service import fetch_sales_data

router = APIRouter(prefix="/take", tags=["take"])

@router.get("/salesdata/")
async def getuserid(db: Session = Depends(get_db), request: Request = None):
    sales = await fetch_sales_data(db=db)

    message_data = {
        "event": "sales_data_viewed",
        "count": len(sales.items()),
        "user_id": getattr(request.state, "user_id", "anonymous")
    }

    message_body = json.dumps(message_data).encode()

    exchange = request.app.state.rmq_exchange    
    await exchange.publish(
        aio_pika.Message(body=message_body),
        routing_key="auth.salesdata.success"
    )

    return sales