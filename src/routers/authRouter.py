from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from schemas.authSchema import TokenResponse, UserRegister
from service.authService import AuthService

router = APIRouter(tags=["auth"], prefix="/auth")


@router.post(
    path="/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
async def register(data: UserRegister):
    db: AsyncSession = Depends(get_db)
    await AuthService.register(user_data=data, session=db)
