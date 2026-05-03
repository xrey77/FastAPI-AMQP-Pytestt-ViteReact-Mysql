import os
import json
import aio_pika # type: ignore
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Request
from PIL import Image
from app.models.user import Users
from sqlalchemy.orm import Session
from app.connection.db import get_db
from app.utils.jwtverification import get_current_user
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession # Import this

router = APIRouter(prefix="/api", tags=["api"])

@router.patch("/uploadpicture/{id}/")
async def uploadProfilepic(id: int,
                           userpic: UploadFile = File(),
                           db: AsyncSession = Depends(get_db),
                           request: Request = None,
                            current_user: dict = Depends(get_current_user)):
    
    img = Image.open(userpic.file)
    ext = "." + img.format

    MAX_SIZE = (100, 100) 
    img.thumbnail(MAX_SIZE)
    path =  "static/users/"
    newfile = "00"+str(id) +  ext
    try:
     os.remove("static/users/00"+str(id)+ext)
    except Exception:
        print(None)
        
    final_filepath = os.path.join(path, newfile)
    img.save(final_filepath)

    result = await db.execute(select(Users).filter(Users.id == id))
    user = result.scalars().first()        
    if user:

        user.userpic = newfile
        await db.commit()    

        message_body = json.dumps({"user_id": current_user["sub"], "event": "user_upload_picture"}).encode()    
        exchange = request.app.state.rmq_exchange    
        await exchange.publish(
            aio_pika.Message(body=message_body),
            routing_key="auth.uploadpicture.success"
        )

        return {"userpic": newfile, "message": "Your profile photo has been successfully changed."}
    
    else:
        raise HTTPException(status_code=500, detail="Error! unable to upload you profile picture.")