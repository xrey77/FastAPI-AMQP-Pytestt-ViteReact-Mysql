import json
import aio_pika # type: ignore
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.connection.db import get_db
from fastapi.responses import JSONResponse
from app.services import auth_service
from app.dtos import registerDto

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register/")
async def createUser(regdto: registerDto.registerDTO,
                     request: Request,
                      db: Session = Depends(get_db)):
    
    user = await auth_service.create_user_account(
        db=db, 
        **regdto.model_dump()
    )

    message_body = json.dumps({"user_id": user.id, "event": "user_account_registration"}).encode()    
    exchange = request.app.state.rmq_exchange
    await exchange.publish(
        aio_pika.Message(body=message_body),
        routing_key="auth.registration.success"
    )

    return JSONResponse(
        status_code=201,
        content={"message": 'You have registered successfully.'},
    )
