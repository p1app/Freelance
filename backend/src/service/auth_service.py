import time

from core.email_message import send_email_message
from core.exceptions import (
    BusinessError,
    ConflictError,
    ForbiddenError,
    UnauthorizedError,
)
from core.security import (
    JWTUser,
    create_access_token,
    create_refresh_token,
    get_password_hash,
    redis_client,
    verify_password,
)
from repository.user_repo import UserRepository
from schemas.auth_schema import (
    TokenResponse,
    UserLogin,
    UserRegister,
    UserRegisterNoPass,
)
from sqlalchemy.ext.asyncio import AsyncSession


class AuthService:
    @classmethod
    async def register(
        cls, session: AsyncSession, user_data: UserRegister
    ) -> TokenResponse:
        username_exists = await UserRepository.get_by_username(
            session=session, username=user_data.username
        )
        if username_exists is not None:
            raise BusinessError("Username already exists")

        email_exists = await UserRepository.get_by_email(
            session=session, email=user_data.email
        )
        if email_exists is not None:
            raise BusinessError("Email already exists")

        hashed_password = get_password_hash(user_data.password)
        created_user = await UserRepository.create(
            session=session,
            hashed_password=hashed_password,
            user_data=UserRegisterNoPass(
                username=user_data.username,
                email=user_data.email,
                role=user_data.role,
                fullname=user_data.fullname,
            ),
        )

        payload = JWTUser(id=created_user.id, role=created_user.role)
        access = create_access_token(payload)
        refresh = create_refresh_token(payload)
        try:
            send_email_message.delay(user_data.email, user_data.username)
        except Exception as e:  # noqa: BLE001
            raise ConflictError(f"error when sending email message {e}")
        return TokenResponse(access_token=access, refresh_token=refresh)

    @classmethod
    async def login(cls, session: AsyncSession, login_data: UserLogin) -> TokenResponse:
        user = await UserRepository.get_by_username(
            username=login_data.username, session=session
        )
        if user is None or not verify_password(
            plain_password=login_data.password, hashed_password=user.hashed_password
        ):
            raise UnauthorizedError("Invalid username or password")

        if user.is_active == False:
            raise ForbiddenError("User is blocked")

        payload = JWTUser(id=user.id, role=user.role)
        access = create_access_token(payload)
        refresh = create_refresh_token(payload)

        return TokenResponse(access_token=access, refresh_token=refresh)

    @classmethod
    async def refresh(
        cls, session: AsyncSession, jwt_user: JWTUser | None
    ) -> TokenResponse:
        if jwt_user is None:
            raise ForbiddenError("Token not available")
        user = await UserRepository.get_by_id(session=session, user_id=jwt_user.id)
        if user is None or not user.is_active:
            raise UnauthorizedError("User not found or blocked")

        jwt_user_new = JWTUser(id=user.id, role=user.role)
        access_token = create_access_token(jwt_user_new)
        refresh_token = create_refresh_token(jwt_user_new)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    @classmethod
    async def logout(cls, raw_jwt: dict | None):
        if raw_jwt is None:
            raise ForbiddenError("token is not valid")
        jti: str = raw_jwt.get("jti")  # type: ignore
        exp: int = raw_jwt.get("exp")  # type: ignore
        now = int(time.time())
        ttl = exp - now

        if ttl > 0:
            redis_client.set(f"revoked_token:{jti}", "true", ex=ttl)
        return True
