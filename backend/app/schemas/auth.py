from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class TokenType(StrEnum):
    access = "access"
    refresh = "refresh"


class AccessTokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    jti: UUID = Field(default_factory=uuid4)
    user_id: str
    exp: int
    fullname: str | None = None
    scopes: list[str]
    type: TokenType = TokenType.access
