from fastapi import APIRouter, HTTPException, status

router = APIRouter()

_DEPRECATED = (
    "Đăng ký/đăng nhập và session được xử lý bởi Better Auth (frontend). "
    "Backend dùng chung schema PostgreSQL với frontend/db/schema.ts (user, session, account, verification)."
)


@router.post("/register", status_code=status.HTTP_410_GONE)
async def register_deprecated() -> None:
    raise HTTPException(status_code=status.HTTP_410_GONE, detail=_DEPRECATED)


@router.post("/login", status_code=status.HTTP_410_GONE)
async def login_deprecated() -> None:
    raise HTTPException(status_code=status.HTTP_410_GONE, detail=_DEPRECATED)


@router.post("/refresh-access-token", status_code=status.HTTP_410_GONE)
async def refresh_access_token_deprecated() -> None:
    raise HTTPException(status_code=status.HTTP_410_GONE, detail=_DEPRECATED)


@router.post("/logout", status_code=status.HTTP_410_GONE)
async def logout_deprecated() -> None:
    raise HTTPException(status_code=status.HTTP_410_GONE, detail=_DEPRECATED)


@router.post("/logout-all", status_code=status.HTTP_410_GONE)
async def logout_all_deprecated() -> None:
    raise HTTPException(status_code=status.HTTP_410_GONE, detail=_DEPRECATED)
