import json
import aio_pika # type: ignore
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.connection.db import get_db
from app.models.product import Products
from sqlalchemy import select, func

router = APIRouter(prefix="/take", tags=["take"])

@router.get("/products/report")
async def productReport(db: Session = Depends(get_db), request: Request = None):
    query = (select(Products))
    result = await db.execute(query)
    products = result.scalars().all()    

    message_data = {
        "event": "product_report_viewed",
        "count": len(products),  # Fixed: removed .items()
        "user_id": getattr(request.state, "user_id", "anonymous")
    }

    message_body = json.dumps(message_data).encode()

    exchange = request.app.state.rmq_exchange    
    await exchange.publish(
        aio_pika.Message(body=message_body),
        routing_key="auth.productreport.success"
    )

    return products
