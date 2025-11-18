from datetime import timedelta, datetime
from uuid import UUID
import bcrypt
import jwt

from app.core.config import settings
from app.schemas.auth import TokenPayload
from app.services.user import UserService

def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_acces_token(data, expires_delta: int | None) -> str:
    exp = datetime.now() + timedelta(minutes=expires_delta if expires_delta else settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": exp})
    access_token = jwt.encode(data, settings.SECRET_KEY, algorithm='HS256')

    return access_token

def create_token(user_id: UUID, expires_delta: int | None = None) -> TokenPayload:
    exp = datetime.now() + timedelta(minutes=expires_delta if expires_delta else settings.ACCESS_TOKEN_EXPIRE_MINUTES)
