import json
import aio_pika # type: ignore
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.connection.db import get_db
from fastapi.responses import JSONResponse
from app.services import auth_service
from app.dtos import loginDto

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login/")
async def loginUser(
    logindto: loginDto.loginDTO, 
    request: Request,
    db: Session = Depends(get_db)
):
    user = await auth_service.user_account_login(db=db, **logindto.model_dump())

    # 1. Prepare message
    message_body = json.dumps({"user_id": user["id"], "event": "user_logged_in"}).encode()    

    # 2. Get the exchange from app state
    exchange = request.app.state.rmq_exchange
    
    # 3. Publish to topic (e.g., 'auth.login.success')
    await exchange.publish(
        aio_pika.Message(body=message_body),
        routing_key="auth.login.success"
    )

    return JSONResponse(content={"user": user}, status_code=200)