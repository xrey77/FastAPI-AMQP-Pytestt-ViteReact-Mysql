from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List

class UserSchema(BaseModel):
    id: int
    firstname: str
    lastname: str
    email: str
    mobile: str
    username: str
    password: str
    roles: str
    isactivated: int
    isblocked: int
    mailtoken: int
    secret: Optional[str] = None 
    qrcodeurl: Optional[str] = None 
    userpic: str
    created_at: datetime = Field(..., description="Timestamp of user creation")
    updated_at: datetime | None = Field(None, description="Timestamp of last update")

    class Config:
        from_attributes = True # Enables Pydantic to read ORM models