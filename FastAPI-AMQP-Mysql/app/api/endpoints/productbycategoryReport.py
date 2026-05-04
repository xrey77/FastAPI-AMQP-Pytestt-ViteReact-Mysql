import json
import aio_pika # type: ignore
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session, joinedload
from app.connection.db import get_db
from app.models.product import Category
from sqlalchemy import select

router = APIRouter(prefix="/take", tags=["take"])

@router.get("/productsbycategory/report")
async def generate_product_report(db: Session = Depends(get_db), request: Request = None):

    query = (
        select(Category)
        .options(joinedload(Category.products)) 
    )
    
    result = await db.execute(query)
    categories = result.unique().scalars().all() 

    message_data = {
        "event": "product_category_viewed",
        "count": len(categories),
        "user_id": getattr(request.state, "user_id", "anonymous")
    }

    message_body = json.dumps(message_data).encode()

    exchange = request.app.state.rmq_exchange    
    await exchange.publish(
        aio_pika.Message(body=message_body),
        routing_key="auth.productcategory.success"
    )

    return categories
