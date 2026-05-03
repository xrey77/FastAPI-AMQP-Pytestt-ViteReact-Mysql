from pydantic import BaseModel

class passwordDTO(BaseModel):
    password: str
