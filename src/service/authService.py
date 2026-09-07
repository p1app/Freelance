from core.security import get_password_hash, create_access_token, create_refresh_token, JWTUser, verify_password
from core.email_message import send_email_message

from sqlalchemy.ext.asyncio import AsyncSession

from schemas.authSchema import TokenResponse, UserRegister, UserLogin
from dao.UserDAO import UserDAO
from core.exceptions import BusinessError, UnauthorizedError, ForbiddenError
from db.models.userModel import User


class AuthService:

    @classmethod
    async def register(cls, session: AsyncSession, user_data: UserRegister) -> TokenResponse:
        username = await UserDAO.get_by_username(session=session, username=user_data.username)
        if username is not None:
            raise BusinessError("Username already exists")

        email = await UserDAO.get_by_email(session=session, email=user_data.email)
        if email is not None:
            raise BusinessError("Email already exists")
        
        user_data.password = get_password_hash(user_data.password)
        created_user = await UserDAO.create(session=session, user_data=user_data)

        payload = JWTUser(id=created_user.id, role=created_user.role)
        access = create_access_token(payload)
        refresh = create_refresh_token(payload)

        send_email_message.delay(user_data.email, user_data.username)
        return TokenResponse(access_token=access, refresh_token=refresh)

    @classmethod
    async def login(cls,session: AsyncSession, login_data: UserLogin) -> TokenResponse:
        user = await UserDAO.get_by_username(username=login_data.username, session=session)
        if user is None or not verify_password(plain_password=login_data.password, hashed_password=user.hashed_password):
            raise UnauthorizedError("Invalid username or password")

        if user.is_active == False:
            raise ForbiddenError("User is blocked")

        payload = JWTUser(id=user.id, role=user.role)
        access = create_access_token(payload)
        refresh = create_refresh_token(payload)
        
        return TokenResponse(access_token=access, refresh_token=refresh)


    @classmethod
    async def refresh(cls, current_user: User) -> TokenResponse:
        if not current_user.is_active:
            raise ForbiddenError("User is blocked")

        jwt_user = JWTUser(id=current_user.id, role=current_user.role)
        access_token = create_access_token(jwt_user)
        refresh_token = create_refresh_token(jwt_user)

        return TokenResponse(access_token=access_token,refresh_token=refresh_token)

    @classmethod
    async def logout(cls) -> dict:
        return {"message": "Logged out successfully"}
