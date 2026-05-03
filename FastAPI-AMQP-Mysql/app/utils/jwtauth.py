import os
import jwt
from dotenv import load_dotenv

load_dotenv() 

SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM")

def decode_token(token: str):
    try:
        # This will verify expiration and signature automatically
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None
