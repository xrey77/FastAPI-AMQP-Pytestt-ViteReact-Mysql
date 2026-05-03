from pydantic import BaseModel, EmailStr
from typing import Optional
from pydantic import BaseModel, ConfigDict

class UserResponse(BaseModel):
    id: int
    firstname: str
    lastname: str
    email: EmailStr
    mobile: Optional[str] = None
    username: str
    qrcodeurl: Optional[str] = None
    userpic: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)