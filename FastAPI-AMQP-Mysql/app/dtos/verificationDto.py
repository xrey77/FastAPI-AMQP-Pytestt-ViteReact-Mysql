from pydantic import BaseModel

class verificationDTO(BaseModel):
    otp: str
