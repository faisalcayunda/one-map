from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.factory import Factory
from app.schemas.token_schema import RefreshTokenSchema, Token
from app.schemas.user_schema import UserSchema
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/auth/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), auth_service: AuthService = Depends(Factory().get_auth_service)
):
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await auth_service.create_tokens(user.id)


@router.post("/auth/logout")
async def logout(
    current_user: UserSchema = Depends(get_current_active_user),
    auth_service: AuthService = Depends(Factory().get_auth_service),
):
    await auth_service.logout(str(current_user.id))


@router.post("/auth/refresh", response_model=Token)
async def refresh_token(
    refresh_token: RefreshTokenSchema, auth_service: AuthService = Depends(Factory().get_auth_service)
):
    return await auth_service.refresh_token(refresh_token.refresh_token)


@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: UserSchema = Depends(get_current_active_user)):
    return current_user
