import os
import time
import jwt
import pyotp
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user import Users
from app.models.user import Department
from app.models.user import Role
from app.utils.hashing import Hasher
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.create_access_token import create_access_token
from sqlalchemy import select  # Add this import
from sqlalchemy.orm import joinedload

async def create_user_account(db: Session, firstname: str, lastname: str, email: str, mobile: str, username: str, password: str):

    result = await db.execute(select(Users).filter(Users.email == email))        
    findEmail = result.scalars().first()    
    if findEmail is not None:
        raise HTTPException(status_code=404, detail="Email Address is already taken.")

    result = await db.execute(select(Users).filter(Users.username == username))    
    findUsername = result.scalars().first()    
    if findUsername is not None:
        raise HTTPException(status_code=404, detail="Username is already taken.")

    hash = Hasher.get_password_hash(password)

    user = Users(
        firstname=firstname,
        lastname=lastname,
        email=email,
        mobile=mobile,
        username=username,
        password=hash,
        role_id = 2,
        department_id = 2,
        userpic='pix.png')
    db.add(user)
    db.commit()    
    return user

async def user_account_login(db: Session, username: str, password: str):
    query = (
        select(Users)
        .options(joinedload(Users.department), joinedload(Users.role))
        .filter(Users.username == username)
    )
    
    result = await db.execute(query)
    user = result.scalars().first()    
    if user:
        if Hasher.verify_password(password, user.password):
            
            payload = {
                "sub": str(user.id),
                "userid": user.email
            }
            token =  create_access_token(payload)

            return { 
                'id': user.id,
                'firstname': user.firstname,
                'lastname': user.lastname,
                'email': user.email,
                'mobile': user.mobile,
                'department': user.department.dept_name if user.department else None,                
                'role': user.role.name if user.role else None,                
                'username': user.username,
                'isactivated': user.isactivated,
                'isblocked': user.isblocked,
                'userpic': user.userpic,
                'qrcodeurl': user.qrcodeurl,
                'token': token,
                'message': 'You have logged-in successfully.'
            }       
             
        else:
            raise HTTPException(status_code=404, detail="Invalid Password, please try again.")                
    else:
        raise HTTPException(status_code=404, detail="Username not found, please register.")                
    

async def mfa_otp_verification(db: AsyncSession, user_id: int, otp: str) -> str:
    query = (
        select(Users)
        .options(joinedload(Users.department), joinedload(Users.role))
        .filter(Users.id == user_id)
    )
    
    result = await db.execute(query)    
    user = result.scalars().first()    

    if user.secret is None:
        raise HTTPException(status_code=404, detail="Multi-Factor Authenticator is not yet activated.")   

    if user is not None:
        totp = pyotp.TOTP(user.secret)
        isOk = totp.verify(otp)        
        if isOk:
            return user.username
        else:        
            return None
    else:
        raise HTTPException(status_code=404, detail="User not found.")   
