from pydantic import BaseModel

class profileDTO(BaseModel):
    firstname: str
    lastname: str
    mobile: str
