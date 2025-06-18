from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db
from app.schemas.schemas import TokenModel, UserResponse, UserCreate
from app.repository.users import get_user_by_email, create_user, update_token
from app.services.auth import auth_service
from app.services.email import send_verification_email

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/login", response_model=TokenModel)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_email(form_data.username, db)
    if not user or not auth_service.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = auth_service.create_access_token(data={"sub": user.email})
    refresh_token = auth_service.create_refresh_token(data={"sub": user.email})
    await update_token(user, refresh_token, db)

    return TokenModel(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_create: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    existing = await get_user_by_email(user_create.email, db)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    hashed = auth_service.hash_password(user_create.password)
    new_user = await create_user(user_create, hashed, db)
    token = auth_service.create_access_token(data={"sub": new_user.email})
    background_tasks.add_task(send_verification_email, new_user.email, token)

    return new_user