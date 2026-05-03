import json
import aio_pika # type: ignore
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.connection.db import get_db
from fastapi.responses import JSONResponse
from app.dtos import profileDto
from app.services.user_service import user_update_profile
from app.utils.jwtverification import get_current_user

router = APIRouter(prefix="/api", tags=["api"])

@router.patch("/updateprofile/{id}/")
async def updateUserProfile(id: int, 
                           profiledto: profileDto.profileDTO, 
                           db: Session = Depends(get_db),
                           request: Request = None,
                            current_user: dict = Depends(get_current_user)):
    await user_update_profile(
        db=db, 
        user_id=id,
        **profiledto.model_dump() 
    )

    message_body = json.dumps({"user_id": current_user["sub"], "event": "user_update_profile"}).encode()    
    exchange = request.app.state.rmq_exchange    
    await exchange.publish(
        aio_pika.Message(body=message_body),
        routing_key="auth.updateprofile.success"
    )    

    return JSONResponse(
        content={"message": "You have updated your profile successfully."},
        status_code=200
    )
