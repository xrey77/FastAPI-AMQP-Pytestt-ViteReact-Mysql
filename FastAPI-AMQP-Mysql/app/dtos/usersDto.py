from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional

class UserDisplay(BaseModel):
    id: int
    firstname: str
    lastname: str
    username: str
    email: str
    mobile: Optional[str]
    userpic: Optional[str]
    role_id: Optional[int] = None
    department_id: Optional[int] = None    
    isactivated: int
    isblocked: int
    created_at: Optional[datetime] = None    
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)    
    # class Config:
    #     from_attributes = True

class PaginatedUsersResponse(BaseModel):
    page: int
    totpage: int
    totalrecords: int
    users: List[UserDisplay]
