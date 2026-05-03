import json
import aio_pika # type: ignore
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.connection.db import get_db
from app.services.user_service import fetch_all_users
from app.dtos.usersDto import PaginatedUsersResponse
from app.utils.jwtverification import get_current_user

router = APIRouter(prefix="/api", tags=["api"])

@router.get("/getusers/{page}/", response_model=PaginatedUsersResponse)
async def getusers(
    page: int = 1, 
    db: Session = Depends(get_db),
    request: Request = None,
    current_user: dict = Depends(get_current_user)
):
    users = await fetch_all_users(db=db, page=page)
    message_body = json.dumps({"user_id": current_user['sub'], "event": "get_all_users"}).encode()    
    exchange = request.app.state.rmq_exchange
    
    await exchange.publish(
        aio_pika.Message(body=message_body),
        routing_key="auth.getallusers.success"
    )

    return users;

