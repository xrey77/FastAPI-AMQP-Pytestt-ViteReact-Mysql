from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, condecimal
from typing import Optional, List
from decimal import Decimal
from typing import Annotated

class ProductSchema(BaseModel):
    id: int
    catetory: str
    descriptions: str
    qty: int
    unit: str
    costprice: Annotated[Decimal, Field(max_digits=10, decimal_places=2)]
    sellprice: Annotated[Decimal, Field(max_digits=10, decimal_places=2)]
    saleprice: Annotated[Decimal, Field(max_digits=10, decimal_places=2)]    
    productpicture: str
    alertstocks: int
    criticalstocks: int
    created_at: datetime = Field(..., description="Timestamp of user creation")
    updated_at: datetime | None = Field(None, description="Timestamp of last update")

    class Config:
        from_attributes = True # Enables Pydantic to read ORM models