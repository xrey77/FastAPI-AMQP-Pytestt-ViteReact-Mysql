from sqlalchemy import Column, func, Integer,  DateTime, Numeric
from app.connection.db import Base

class Sales(Base):
    __tablename__ = "sales"    
    id = Column(Integer, primary_key=True, index=True)    
    salesamount = Column(Numeric(10, 2), server_default="0.00", nullable=False) 
    salesdate = Column(DateTime(timezone=True), server_default=func.now())
    
