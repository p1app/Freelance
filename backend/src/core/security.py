from datetime import timedelta

from core.database import get_db
from core.enums import RoleEnum
from core.exceptions import ForbiddenError, NotFoundError, UnauthorizedError
from core.settings import config as Config
from fastapi import Depends # dishka

from fastapi_jwt_harmony import JWTHarmony, JWTHarmonyDep, JWTHarmonyRefresh
from models.user_model import User
from passlib.context import CryptContext
from pydantic import BaseModel
from repository.user_repo import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


class JWTUser(BaseModel):
    id: int
    role: RoleEnum


JWTHarmony.configure(
    JWTUser,
    {
        "secret_key": Config.security.secret_key,
        "algorithm": Config.security.algorithm,
        "access_token_expires": timedelta(minutes=Config.security.access_token_expires),
        "refresh_token_expires": timedelta(days=Config.security.refresh_token_expires),
        "token_location": {"headers"},
        "header_name": "Authorization",
        "header_type": "Bearer",
    },
)


def create_access_token(jwtuser: JWTUser) -> str:
    auth = JWTHarmony[JWTUser]()
    return auth.create_access_token(user_claims=jwtuser)


def create_refresh_token(jwtuser: JWTUser) -> str:
    auth = JWTHarmony[JWTUser]()
    return auth.create_refresh_token(user_claims=jwtuser)


async def get_current_user(
    db: AsyncSession = Depends(get_db),  # noqa: B008
    Authorize: JWTHarmony[JWTUser] = Depends(JWTHarmonyDep),  # noqa: B008
) -> User:
    jwt_user = Authorize.user_claims
    if not jwt_user:
        raise UnauthorizedError("Invalid token")

    user = await UserRepository.get_by_id(session=db, user_id=jwt_user.id)
    if not user:
        raise NotFoundError("User not found")
    return user


async def get_current_user_optional(
    db: AsyncSession = Depends(get_db),  # noqa: B008
    Authorize: JWTHarmony[JWTUser] = Depends(JWTHarmonyDep),  # noqa: B008
) -> User | None:
    jwt_user = Authorize.user_claims
    if not jwt_user:
        raise UnauthorizedError("Invalid token")

    user = await UserRepository.get_by_id(session=db, user_id=jwt_user.id)
    if not user:
        return None
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),  # noqa: B008
) -> User:
    if not current_user.is_active:
        raise ForbiddenError("User is blocked")
    return current_user


async def get_current_client(
    current_user: User = Depends(get_current_active_user),  # noqa: B008
) -> User:
    if current_user.role != RoleEnum.CLIENT:
        raise ForbiddenError("Client role required")
    return current_user


async def get_current_freelancer(
    current_user: User = Depends(get_current_active_user),  # noqa: B008
) -> User:
    if current_user.role != RoleEnum.FREELANCER:
        raise ForbiddenError("Freelancer role required")
    return current_user


async def get_current_admin(
    current_user: User = Depends(get_current_active_user),  # noqa: B008
) -> User:
    if current_user.role != RoleEnum.ADMIN:
        raise ForbiddenError("Admin role required")
    return current_user


async def get_current_user_refresh(
    db: AsyncSession = Depends(get_db),  # noqa: B008
    Authorize: JWTHarmony[JWTUser] = Depends(JWTHarmonyRefresh),  # noqa: B008
) -> User:
    jwt_user = Authorize.user_claims
    if not jwt_user:
        raise UnauthorizedError("Invalid refresh token")

    user = await UserRepository.get_by_id(session=db, user_id=jwt_user.id)
    if not user:
        raise NotFoundError("User not found")
    if user.is_active != True:
        raise NotFoundError("User is blocked")
    return user
