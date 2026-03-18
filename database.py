# from sqlalchemy import create_engine
# from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# DBA url
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./blog.db"

# Connection to the DBA
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# This is a factory that creates session
# Sessions are transactions to the database where each req has it's own session 
# commits and flush are false because we need to control when changes are commited
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Defines a declarative base class where all sqlalchemy models inherit
class Base(DeclarativeBase):
    pass


# A dependency function that provides session to our routes 
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session











