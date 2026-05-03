import json
import aio_pika # type: ignore
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.connection.db import get_db
from app.services.user_service import fetch_user_by_id
from app.utils.jwtverification import get_current_user
from app.dtos.userResponse import UserResponse
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api", tags=["api"])

@router.get("/getuserid/{id}/", response_model=UserResponse)
async def getuserid(
    id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    request: Request = None
):
    user_dto = await fetch_user_by_id(db, id)

    message_body = json.dumps({
        "user_id": user_dto.id, 
        "event": "get_user_id"
    }).encode()        
    exchange = request.app.state.rmq_exchange

    await exchange.publish(
        aio_pika.Message(body=message_body),
        routing_key="auth.getuserid.success"
    )

    return user_dto