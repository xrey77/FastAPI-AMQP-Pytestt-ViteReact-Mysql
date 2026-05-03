from fastapi import Depends, HTTPException
from jwt import PyJWTError
from fastapi.security import OAuth2PasswordBearer
from app.utils.jwtauth import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub") or payload.get("user_id") # Try multiple common keys
        print(user_id)

        if user_id is None:
            # Debug print
            raise HTTPException(status_code=401, detail="Token missing sub")
        return payload
    except PyJWTError as e:
        # This will show if the token is expired or has an invalid signature
        raise HTTPException(status_code=401, detail=f"Token error: {str(e)}")
