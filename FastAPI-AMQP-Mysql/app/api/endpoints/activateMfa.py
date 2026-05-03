import json
import aio_pika # type: ignore
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.connection.db import get_db
from fastapi.responses import JSONResponse
from app.dtos import activationDto
from app.services.user_service import mfa_activate_totpd
from app.utils.jwtverification import get_current_user

router = APIRouter(prefix="/api", tags=["api"])

@router.patch("/activatemfa/{id}/")
async def mfaActivation(id: int, 
                        activationdto: activationDto.activationDTO, 
                        db: Session = Depends(get_db),
                        request: Request = None,
                        current_user: dict = Depends(get_current_user)
                        ) -> dict:

    isQrcode = await mfa_activate_totpd(
        db=db, 
        user_id=id,
        **activationdto.model_dump() 
    )

    if isQrcode is not None:

        message_body = json.dumps({"user_id": current_user["sub"], "event": "user_mfa_activation"}).encode()    
        exchange = request.app.state.rmq_exchange    
        await exchange.publish(
            aio_pika.Message(body=message_body),
            routing_key="auth.mfaactivation.success"
        )

        return JSONResponse(
            content={
                "qrcodeurl": isQrcode,
                "message": "Multi-Factor Authenticator is enabled successfully."},
            status_code=200
        )    
    else:

        message_body = json.dumps({"user_id": current_user["sub"], "event": "user_mfa_activation"}).encode()    
        exchange = request.app.state.rmq_exchange    
        await exchange.publish(
            aio_pika.Message(body=message_body),
            routing_key="auth.mfaactivation.success"
        )

        return JSONResponse(
            content={"message": "Multi-Factor Authenticator is disabled successfully."},
            status_code=200
        )
    
