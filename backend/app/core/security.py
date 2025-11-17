from datetime import timedelta, datetime
from uuid import UUID
import bcrypt

from app.core.config import settings

def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_acces_token(jti: UUID, user_id, fullname: str, expires_delta: int = 15) -> str:

    expires_delta = datetime.now() + timedelta(minutes=expires_delta)
