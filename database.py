from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# DBA url
SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"

# Connection to the DBA
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# This is a factory that creates session
# Sessions are transactions to the database where each req has it's own session 
# commits and flush are false because we need to control when changes are commited
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Defines a declarative base class where all sqlalchemy models inherit
class Base(DeclarativeBase):
    pass


# A dependency function that provides session to our routes 
def get_db():
    with SessionLocal() as db:
        yield db











