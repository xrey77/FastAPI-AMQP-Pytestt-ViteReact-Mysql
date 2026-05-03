import io
import math
from sqlalchemy.orm import Session
from app.models.user import Users
from fastapi import HTTPException, logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import pyotp
import qrcode
import base64
from app.utils.hashing import Hasher
from app.dtos.userResponse import UserResponse
from sqlalchemy.orm import joinedload
from sqlalchemy import select, func
from app.dtos.updateDto import UpdateDTO

async def fetch_user_by_id(db: AsyncSession, user_id: int) -> UserResponse:
    query = (
        select(Users)
        .options(joinedload(Users.department), joinedload(Users.role))
        .filter(Users.id == user_id)
    )
    
    result = await db.execute(query)

    user = result.scalars().first()    
    if not user:
        raise HTTPException(status_code=404, detail="No record(s) found.")    
    
    return UserResponse.model_validate(user)

async def fetch_all_users(db: Session, page: int):
    try:
        per_page = 5
        offset = (page - 1) * per_page
        
        # 1. Use select for the count to keep it consistent
        total_recs = await db.scalar(select(func.count(Users.id)))
        total_pages = math.ceil(total_recs / per_page)

        query = (
            select(Users)
            .options(joinedload(Users.department), joinedload(Users.role))
            .offset(offset)
            .limit(per_page)
        )
    
        result = await db.execute(query)
        # 2. Extract the actual user objects
        users = result.scalars().all()
        
        # 3. Check if the list is empty
        if not users:
            raise HTTPException(status_code=404, detail="No record(s) found.")

        return {
            "page": page, 
            "totpage": total_pages, 
            "totalrecords": total_recs, 
            "users": users
        }    
    except Exception as e:
        logger.exception(f"Error fetching users: {e}")        
        raise # Re-raising ensures the router can catch it or FastAPI's handler takes over

async def user_update_profile(db: AsyncSession, user_id: int, firstname: str, lastname: str, mobile: str):
    query = (
        select(Users)
        .options(joinedload(Users.department), joinedload(Users.role))
        .filter(Users.id == user_id)
    )
    
    result = await db.execute(query)
    user = result.scalars().first()

    if user is not None:
        user.firstname = firstname
        user.lastname = lastname 
        user.mobile = mobile
        
        # Use await for commit
        db.commit()    
        return user
    else:
        raise HTTPException(status_code=500, detail="User not found.")
            

async def user_update_password(db: AsyncSession, user_id: int, password: str):
    query = (
        select(Users)
        .options(joinedload(Users.department), joinedload(Users.role))
        .filter(Users.id == user_id)
    )
    
    user = await db.execute(query)

    if user is not None:
        hash = Hasher.get_password_hash(password)
        user.password = hash
        db.commit()
    else:
        raise HTTPException(status_code=500, detail="User not found.")


async def mfa_activate_totpd(db: AsyncSession, user_id: int, TwoFactorEnabled: bool) -> str:
    query = (
        select(Users)
        .options(joinedload(Users.department), joinedload(Users.role))
        .filter(Users.id == user_id)
    )
    
    result = await db.execute(query)
    user = result.scalar_one_or_none()     
    if not user:
        raise HTTPException(status_code=500, detail="User not found.")


    if TwoFactorEnabled:
        email = user.email
        pytopsecret = pyotp.random_base32()
        provisioning_uri = pyotp.totp.TOTP(pytopsecret).provisioning_uri(
            name=email, 
            issuer_name="BARCLAYS BANK"
        )

        # QR Generation
        img = qrcode.make(provisioning_uri)            
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        qrcodeb64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        user.secret = pytopsecret
        user.qrcodeurl = qrcodeb64
        
        await db.commit()
        full_qrcode_uri = f"data:image/png;base64,{qrcodeb64}"        
        return full_qrcode_uri
        
    else:
        dto_instance = UpdateDTO(secret=None, qrcodeurl=None)
        update_data = dto_instance.model_dump(exclude_unset=True)        

        for key, value in update_data.items():
            setattr(user, key, value)
        try:
            await db.commit()
            return None
        except Exception as e:
            await db.rollback()
            raise e            