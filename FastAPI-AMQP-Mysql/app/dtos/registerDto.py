from pydantic import BaseModel

class registerDTO(BaseModel):
    firstname: str
    lastname: str
    email: str
    mobile: str
    username: str
    password: str
