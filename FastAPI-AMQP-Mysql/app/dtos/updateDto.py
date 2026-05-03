# app/dtos/updatedto.py
from pydantic import BaseModel
from typing import Optional

class UpdateDTO(BaseModel):
    secret: Optional[str] = None 
    qrcodeurl: Optional[str] = None
