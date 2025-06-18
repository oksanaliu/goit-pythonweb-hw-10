from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.services.auth import auth_service
from app.repository.users import update_avatar as repo_update_avatar
from app.schemas.schemas import UserResponse, UserUpdate
from app.database.db import get_db
from app.services.cloudinary_service import upload_avatar

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.get(
    "/me",
    response_model=UserResponse,
)
@limiter.limit("5/minute")
async def me(
    request: Request,
    current_user=Depends(auth_service.get_current_user),
):
    return current_user

@router.patch(
    "/me/avatar",
    response_model=UserResponse,
    summary="Оновити аватар користувача"
)
async def patch_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(auth_service.get_current_user),
):
    url = await upload_avatar(file)
    updated = await repo_update_avatar(current_user, url, db)
    return updated

@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Оновити інші поля профілю"
)
async def patch_me(
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(auth_service.get_current_user),
):
    if body.avatar_url:
        updated = await repo_update_avatar(current_user, body.avatar_url, db)
        return updated
    return current_user
