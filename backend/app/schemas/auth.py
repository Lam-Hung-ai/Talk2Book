from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.schemas.role import RoleEnum


class TokenType(str, Enum):
    access = "access"
    refresh = "refresh"

class AccessTokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginSchema(BaseModel):
    identity: str
    password: str
    require_scope: RoleEnum = RoleEnum.user

class TokenPayload(BaseModel):
    jti: UUID = Field(default_factory=uuid4)
    user_id: UUID
    exp: int
    fullname: str | None = None
    scopes: list[str]
    type: TokenType = TokenType.access
