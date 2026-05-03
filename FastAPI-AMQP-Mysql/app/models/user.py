from sqlalchemy import Column, func, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.connection.db import Base

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), unique=True, nullable=False)

    users = relationship("Users", back_populates="role")

class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    dept_name = Column(String(20), unique=True, nullable=False)

    users = relationship("Users", back_populates="department")

class Users(Base):
    __tablename__ = "users"    
    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String(20), nullable=False)
    lastname = Column(String(20), nullable=False)
    email = Column(String(255), unique=True)
    mobile = Column(String(20))
    username = Column(String(20), unique=True)    
    # username = Column(String(20), unique=True, collation='utf8mb4_bin')    

    password = Column(String(255), nullable=False)
    
    isactivated = Column(Integer, default=1)
    isblocked = Column(Integer, default=0)
    mailtoken = Column(Integer, default=0)
    secret = Column(Text)
    qrcodeurl = Column(Text)
    userpic = Column(String(255) , default='pix.png')
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())        

    role_id = Column(Integer, ForeignKey("roles.id"))    
    department_id = Column(Integer, ForeignKey("departments.id"))    

    role = relationship("Role", back_populates="users")
    department = relationship("Department", back_populates="users")
