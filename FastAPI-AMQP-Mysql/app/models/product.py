from sqlalchemy import Column, func, Integer, String, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import relationship
from app.connection.db import Base

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), unique=True, nullable=False)

    products = relationship("Products", back_populates="category_rel")


class Products(Base):
    __tablename__ = "products"    
    id = Column(Integer, primary_key=True, index=True)    
    descriptions = Column(String(100))
    qty = Column(Integer, default=0, nullable=True)
    unit = Column(String(20))    
    costprice = Column(Numeric(precision=10, scale=2), default=0) 
    sellprice = Column(Numeric(precision=10, scale=2), default=0) 
    saleprice = Column(Numeric(precision=10, scale=2), default=0)    
    productpicture = Column(String(100))
    alertstocks = Column(Integer, default=0, nullable=True)
    criticalstocks = Column(Integer, default=0, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    category_id = Column(Integer, ForeignKey("categories.id"))    
    
    category_rel = relationship("Category", back_populates="products")
