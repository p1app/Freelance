from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import BusinessError, ForbiddenError, NotFoundError
from dao.AdminDAO import AdminDAO
from dao.UserDAO import UserDAO
from db.enums import ProjectStatusEnum, RoleEnum
from db.models.userModel import User as UserModel
from schemas.adminSchema import (
    AdminProjectResponse,
    AdminUserResponse,
    PlatformStatsResponse,
)
from schemas.paginationSchema import PaginatedResponse


def _check_admin_privileges(user: UserModel):
    if user.role != RoleEnum.ADMIN:
        raise ForbiddenError("You aren`t admin")


class AdminService:
    @classmethod
    async def get_all_users(
        cls,
        current_user: UserModel,
        session: AsyncSession,
        role: RoleEnum | None = None,
        page: int = 1,
        page_size: int = 20,
        is_active: bool | None = None,
    ) -> PaginatedResponse[AdminUserResponse]:
        _check_admin_privileges(current_user)
        users, total = await AdminDAO.list_users(
            session=session,
            role=role,
            is_active=is_active,
            page=page,
            page_size=page_size,
        )
        if users is not None:
            validate_data = [AdminUserResponse.model_validate(i) for i in users]
        else:
            validate_data = []
        if total is None:
            total = 0
        return PaginatedResponse(
            items=validate_data,
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size,
        )

    @classmethod
    async def get_user(
        cls, current_user: UserModel, session: AsyncSession, user_id
    ) -> AdminUserResponse:
        _check_admin_privileges(current_user)
        user = await UserDAO.get_by_id(session=session, user_id=user_id)
        if user is None:
            raise NotFoundError("user not found")
        return AdminUserResponse.model_validate(user)

    @classmethod
    async def block_user(
        cls, session: AsyncSession, current_user: UserModel, user_id: int
    ) -> Literal[True]:
        _check_admin_privileges(current_user)
        if current_user.id == user_id:
            raise BusinessError("You cannot block yourself")
        result = await AdminDAO.block_user(session=session, user_id=user_id)
        if result is None:
            raise NotFoundError("User not found")
        return result

    @classmethod
    async def unblock_user(
        cls, session: AsyncSession, current_user: UserModel, user_id: int
    ) -> Literal[True]:
        _check_admin_privileges(current_user)
        result = await AdminDAO.unblock_user(session=session, user_id=user_id)
        if result is None:
            raise NotFoundError("User not found")
        return result

    @classmethod
    async def get_all_projects(
        cls,
        current_user: UserModel,
        session: AsyncSession,
        status: ProjectStatusEnum | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse[AdminProjectResponse]:
        _check_admin_privileges(current_user)
        projects, total = await AdminDAO.list_projects(
            session=session, status=status, page=page, page_size=page_size
        )
        if projects is not None:
            validate_data = [AdminProjectResponse.model_validate(i) for i in projects]
        else:
            validate_data = []
        if total is None:
            total = 0
        return PaginatedResponse(
            items=validate_data,
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size,
        )

    @classmethod
    async def delete_project(
        cls, current_user: UserModel, project_id: int, session: AsyncSession
    ) -> Literal[True]:
        _check_admin_privileges(current_user)
        result = await AdminDAO.delete_project(project_id=project_id, session=session)
        if result is None:
            raise NotFoundError("project not found")
        return result

    @classmethod
    async def get_stats(
        cls, session: AsyncSession, current_user: UserModel
    ) -> PlatformStatsResponse:
        _check_admin_privileges(current_user)
        stats = await AdminDAO.get_stats(session=session)
        if not stats:
            raise NotFoundError("Stats not available")
        return PlatformStatsResponse(**stats)
