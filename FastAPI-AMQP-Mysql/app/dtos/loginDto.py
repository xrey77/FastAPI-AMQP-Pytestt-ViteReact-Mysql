from pydantic import BaseModel

class loginDTO(BaseModel):
    username: str
    password: str
