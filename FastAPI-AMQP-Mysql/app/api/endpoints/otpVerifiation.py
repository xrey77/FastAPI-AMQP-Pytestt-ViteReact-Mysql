import json

from fastapi.responses import JSONResponse
import aio_pika # type: ignore
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.connection.db import get_db
from app.dtos import verificationDto
from app.services.auth_service import mfa_otp_verification
from app.utils.jwtverification import get_current_user

router = APIRouter(prefix="/api", tags=["api"])

@router.patch("/verifyotpcode/{id}/")
async def otpVerification(id: int, 
                          verificationdto: verificationDto.verificationDTO, 
                          db: Session = Depends(get_db), 
                          request: Request = None,
                          current_user: dict = Depends(get_current_user)):

    isValid = await mfa_otp_verification(
        db=db, 
        user_id=id,
        **verificationdto.model_dump()
    )

    if isValid is not None:

        message_body = json.dumps({"user_id": current_user["sub"], "event": "user_otp_verification"}).encode()    
        exchange = request.app.state.rmq_exchange    
        await exchange.publish(
            aio_pika.Message(body=message_body),
            routing_key="auth.otpverification.success"
        )

        return JSONResponse(
            content={
                "username": isValid,
                "message": "OTP code has been validated successfully."},
            status_code=200
        )    
    else:
        raise HTTPException(status_code=404, detail="Invalid OTP code, please get the OTP code from your mobile Google or Microsoft Authenticator.")    
    
