import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
# 1. Add this import
from sqlalchemy.orm import DeclarativeBase 
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "mysql+aiomysql://rey:rey@127.0.0.1:3306/fastapi_rabbitmq"
)

# 2. Define the Base class here
class Base(DeclarativeBase):
    pass

engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,   
    max_overflow=20
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()





# from dotenv import load_dotenv
# import os
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, Session
# from fastapi import Depends
# from typing import Generator
# from sqlalchemy.orm import declarative_base
# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

# load_dotenv() 

# engine = create_engine(os.getenv("SQLALCHEMY_DATABASE_URL"), connect_args={"connect_timeout": 30}, pool_pre_ping=True)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()

# async def get_db():
#     async with AsyncSession(engine) as session:
#         yield session

# # def get_db() -> Generator:    
#     # db = SessionLocal()
#     # try:
#     #     yield db
#     # finally:
#     #     db.close()
