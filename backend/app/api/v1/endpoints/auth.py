from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.api.v1.endpoints.user import get_user_service
from app.core.config import settings
from app.core.security import decode_token
from app.schemas.auth import AccessTokenSchema, LoginSchema, TokenPayload
from app.schemas.user import UserCreate, UserRead
from app.services.auth import AuthService

router = APIRouter()


async def get_auth_service(
    session: AsyncSession = Depends(get_async_session),
) -> AuthService:
    return AuthService(session)


async def _set_refresh_cookie(
    resp: Response, refresh_token: str, max_age: int | None = None
):
    resp.set_cookie(
        key=settings.COOKIE_REFRESH_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        domain=settings.COOKIE_DOMAIN,
        path=settings.COOKIE_PATH,
        max_age=max_age,
    )


async def _clear_refresh_cookie(resp: Response):
    resp.delete_cookie(
        key=settings.COOKIE_REFRESH_NAME,
        domain=settings.COOKIE_DOMAIN,
        # path=settings.COOKIE_PATH,
    )


@router.post("/register", response_model=UserRead, status_code=201)
async def register(payload: UserCreate, user_service=Depends(get_user_service)):
    return await user_service.create_user(payload)


@router.post("/login", response_model=AccessTokenSchema)
async def login(
    req: Request,
    resp: Response,
    form_data: LoginSchema,
    auth_service: AuthService = Depends(get_auth_service),
):
    access, refresh = await auth_service.login(form_data)

    # Đặt refresh token vào cookie HttpOnly
    await _set_refresh_cookie(resp, refresh)

    # Chỉ trả về access token trong body
    return AccessTokenSchema(access_token=access)


@router.post("/refresh-access-token", response_model=AccessTokenSchema)
async def refresh_access_token(req: Request, auth_service: AuthService = Depends(get_auth_service)):
    # Đọc refresh token từ cookie
    refresh_token = req.cookies.get(settings.COOKIE_REFRESH_NAME)
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token cookie")

    access = await auth_service.create_new_access_token(refresh_token=refresh_token)

    return AccessTokenSchema(access_token=access)


@router.post("/logout", status_code=204)
async def logout(
    req: Request, resp: Response, auth_service: AuthService = Depends(get_auth_service)
):
    refresh_cookie = req.cookies.get(settings.COOKIE_REFRESH_NAME)
    if refresh_cookie:
        await auth_service.logout(refresh_cookie)
    await _clear_refresh_cookie(resp)
    return


@router.post("/logout-all", status_code=204)
async def logout_all(
    req: Request, resp: Response, auth_service: AuthService = Depends(get_auth_service)
):
    refresh_token = req.cookies.get(settings.COOKIE_REFRESH_NAME)
    if refresh_token:
        all_user_info: TokenPayload = decode_token(refresh_token)
        await auth_service.logout_all(all_user_info.user_id)
    if resp:
        await _clear_refresh_cookie(resp)
    return
