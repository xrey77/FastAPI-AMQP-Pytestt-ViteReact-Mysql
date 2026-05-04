from decimal import Decimal
from typing import List
from pydantic import BaseModel, ConfigDict

class ProductDisplay(BaseModel):
    id: int
    descriptions: str
    qty: int
    unit: str
    costprice: Decimal
    sellprice: Decimal
    saleprice: Decimal
    productpicture: str
    alertstocks: int
    criticalstocks: int
    
    model_config = ConfigDict(from_attributes=True)    

class PaginatedProductsResponse(BaseModel):
    page: int
    totpage: int
    totalrecords: int
    products: List[ProductDisplay]
