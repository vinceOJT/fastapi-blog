
from datetime import UTC, datetime, timedelta


import jwt
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from config import Settings


password_hash = PasswordHash.recommmended()
oauth2_scheme = OAuth2PasswordBearer(tokenURl="api/users/token")


def hash_password(password:str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password:str, hashed_password:str) -> bool:
    return password_hash.verify(plain_password, hashed_password)










