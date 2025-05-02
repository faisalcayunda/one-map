from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.factory import Factory
from app.models.user_model import UserModel
from app.schemas.token_schema import RefreshTokenSchema, Token
from app.schemas.user_schema import UserSchema
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/login", response_model=Token)
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


@router.post("/logout")
async def logout(
    current_user: UserModel = Depends(get_current_user),
    auth_service: AuthService = Depends(Factory().get_auth_service),
):
    await auth_service.logout(current_user.id)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: RefreshTokenSchema, auth_service: AuthService = Depends(Factory().get_auth_service)
):
    return await auth_service.refresh_token(refresh_token.refresh_token)


@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: UserModel = Depends(get_current_user)):
    return current_user
