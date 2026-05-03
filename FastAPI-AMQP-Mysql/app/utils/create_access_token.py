import os
import time
import jwt
from app.models.user import Users
from dotenv import load_dotenv
load_dotenv()

def create_access_token(payload: dict): 

    payload = {
        "sub": payload['sub'],
        "email": payload['userid'],
        "exp": time.time() + 28800  # 8 hours in seconds
    }

    JWT_SECRET = os.getenv("JWT_SECRET", "your-default-secret-only-for-local")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
                
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token
