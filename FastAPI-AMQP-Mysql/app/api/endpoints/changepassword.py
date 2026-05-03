import json
import aio_pika # type: ignore
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.connection.db import get_db
from fastapi.responses import JSONResponse
from app.dtos import passwordDto
from app.services.user_service import user_update_password
from app.utils.jwtverification import get_current_user

router = APIRouter(prefix="/api", tags=["api"])

@router.patch("/changepassword/{id}/")
async def upateUserPassword(id: int,
                            passworddto: passwordDto.passwordDTO, 
                            db: Session = Depends(get_db),
                            request: Request = None,
                            current_user: dict = Depends(get_current_user)):
    await user_update_password(
        db=db, 
        user_id=id,
        **passworddto.model_dump() 
    )

    message_body = json.dumps({"user_id": current_user["sub"], "event": "user_change_password"}).encode()    
    exchange = request.app.state.rmq_exchange    
    await exchange.publish(
        aio_pika.Message(body=message_body),
        routing_key="auth.changepassword.success"
    )

    return JSONResponse(
        content={"message": "You have changed you password successfully."},
        status_code=200
    )
