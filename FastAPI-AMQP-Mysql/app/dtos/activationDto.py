from pydantic import BaseModel

class activationDTO(BaseModel):
    TwoFactorEnabled: bool
