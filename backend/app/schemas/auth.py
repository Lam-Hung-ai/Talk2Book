from uuid import UUID

from pydantic import BaseModel, Field

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenPayload(BaseModel):
    jti: UUID
    user_id: str
    exp: int
    fullname: str
    email: str
    scopes: list[str]
