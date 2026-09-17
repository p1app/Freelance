from datetime import UTC, datetime
from typing import Literal

from core.enums import ProjectStatusEnum, RoleEnum
from core.exceptions import (
    BusinessError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)
from models.project_model import Project as ProjectModel
from models.user_model import User as UserModel
from repository.project_repo import ProjectRepository
from schemas.pagination_schema import PaginatedResponse
from schemas.project_schema import (
    ProjectCreate,
    ProjectDetailResponse,
    ProjectListFilter,
    ProjectResponse,
    ProjectUpdate,
)
from schemas.proposal_schema import ProposalResponse
from sqlalchemy.ext.asyncio import AsyncSession


def _check_ownership(project: ProjectModel | None, user_id: int) -> ProjectModel:
    if project is None:
        raise NotFoundError("Project not found")
    if project.customer_id != user_id:
        raise ForbiddenError("You do not have ownership rights to this project")
    return project


class ProjectService:
    @classmethod
    async def create_project(
        cls, session: AsyncSession, data: ProjectCreate, customer_id: int
    ) -> ProjectResponse:
        if data.deadline <= datetime.now(UTC):
            raise ValidationError(
                "The deadline must not contain a time shorter than the present time"
            )

        project = await ProjectRepository.create(
            session=session, project_data=data, customer_id=customer_id
        )

        return ProjectResponse.model_validate(project)

    @classmethod
    async def get_project(
        cls, session: AsyncSession, project_id: int
    ) -> ProjectDetailResponse:
        project = await ProjectRepository.get_by_id(
            session=session, project_id=project_id
        )
        if project is None:
            raise NotFoundError("Project not found")
        proposals_valid = [
            ProposalResponse.model_validate(i) for i in project.proposals
        ]

        response = ProjectDetailResponse(
            id=project.id,
            title=project.title,
            description=project.description,
            budget=project.budget,
            deadline=project.deadline,
            category=project.category,
            status=project.status,
            customer_id=project.customer_id,
            freelancer_id=project.freelancer_id,
            created_at=project.created_at,
            customer_name=project.customer.fullname,
            freelancer_name=None,
            proposal_count=None,
            proposals=proposals_valid,
        )
        if project.freelancer_id != None:
            response.freelancer_name = project.freelancer.fullname  # type: ignore
        response.proposal_count = len(project.proposals) if project.proposals else 0

        return response

    @classmethod
    async def update_project(
        cls,
        session: AsyncSession,
        project_id: int,
        data: ProjectUpdate,
        current_user: UserModel,
    ) -> ProjectResponse:
        project = await ProjectRepository.get_by_id(
            session=session, project_id=project_id
        )
        checked_project = _check_ownership(project, current_user.id)

        if checked_project.status != ProjectStatusEnum.DRAFT:
            raise BusinessError(
                "The project cannot be changed to a status other than DRAFT"
            )

        updated_project = await ProjectRepository.update(
            session=session, project_id=project_id, project_data=data
        )
        return ProjectResponse.model_validate(updated_project)

    @classmethod
    async def delete_project(
        cls, session: AsyncSession, current_user: UserModel, project_id: int
    ) -> Literal[True]:
        project = await ProjectRepository.get_by_id(
            session=session, project_id=project_id
        )
        checked_project = _check_ownership(project, current_user.id)

        if checked_project.status not in [
            ProjectStatusEnum.DRAFT,
            ProjectStatusEnum.OPEN,
        ]:
            raise BusinessError(
                "The project cannot be deleted with status other than DRAFT or OPEN"
            )

        result = await ProjectRepository.delete(session=session, project_id=project_id)
        if result is None:
            raise NotFoundError("Project not found")
        return result

    @classmethod
    async def publish_project(
        cls, session: AsyncSession, current_user: UserModel, project_id: int
    ) -> ProjectResponse:
        project = await ProjectRepository.get_by_id(
            session=session, project_id=project_id
        )
        checked_project = _check_ownership(project, current_user.id)

        if checked_project.status != ProjectStatusEnum.DRAFT:
            raise BusinessError("Only DRAFT projects can be published")

        published_project = await ProjectRepository.publish(
            session=session, project_id=project_id
        )
        return ProjectResponse.model_validate(published_project)

    @classmethod
    async def cancel_project(
        cls, session: AsyncSession, current_user: UserModel, project_id: int
    ) -> ProjectResponse:
        project = await ProjectRepository.get_by_id(
            session=session, project_id=project_id
        )
        if project is None:
            raise NotFoundError("Project not found")

        if (
            project.customer_id != current_user.id
            and current_user.role != RoleEnum.ADMIN
        ):
            raise ForbiddenError("You do not have rights to cancel this project")

        if project.status not in [
            ProjectStatusEnum.OPEN,
            ProjectStatusEnum.IN_PROGRESS,
        ]:
            raise BusinessError("Only OPEN or IN_PROGRESS projects can be cancelled")

        cancelled_project = await ProjectRepository.cancel(
            session=session, project_id=project_id
        )
        return ProjectResponse.model_validate(cancelled_project)

    @classmethod
    async def assign_freelancer(
        cls,
        session: AsyncSession,
        current_user: UserModel,
        project_id: int,
        freelancer_id: int,
    ) -> ProjectResponse:
        project = await ProjectRepository.get_by_id(
            session=session, project_id=project_id
        )
        _check_ownership(project, current_user.id)

        if freelancer_id == current_user.id:
            raise BusinessError("The creator of the project cannot be its freelancer")

        updated_project = await ProjectRepository.assign_freelancer(
            session=session, project_id=project_id, freelancer_id=freelancer_id
        )
        return ProjectResponse.model_validate(updated_project)

    @classmethod
    async def list_open_projects(
        cls,
        session: AsyncSession,
        filters: ProjectListFilter,
    ) -> PaginatedResponse[ProjectResponse]:
        projects, total = await ProjectRepository.get_open_projects(
            session=session, page=filters.page, page_size=filters.page_size
        )
        if total == None:
            raise ConflictError("total is None")

        validate_projects = [
            ProjectResponse.model_validate(project) for project in projects
        ]

        return PaginatedResponse(
            items=validate_projects,
            total=total,
            page=filters.page,
            page_size=filters.page_size,
            pages=(total + filters.page_size - 1) // filters.page_size,
        )

    @classmethod
    async def get_my_projects(
        cls, session: AsyncSession, current_user: UserModel, page: int, page_size: int
    ) -> PaginatedResponse[ProjectResponse]:
        projects, total = await ProjectRepository.get_by_customer(
            session=session, customer_id=current_user.id, page=page, page_size=page_size
        )

        validate_projects = [
            ProjectResponse.model_validate(project) for project in projects
        ]

        if total == None:
            raise ConflictError("total is None")

        return PaginatedResponse(
            items=validate_projects,
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size,
        )

    @classmethod
    async def get_working_projects(
        cls, session: AsyncSession, current_user: UserModel, page: int, page_size: int
    ) -> PaginatedResponse[ProjectResponse]:
        projects, total = await ProjectRepository.get_by_freelancer(
            session=session,
            freelancer_id=current_user.id,
            page=page,
            page_size=page_size,
        )

        validate_projects = [
            ProjectResponse.model_validate(project) for project in projects
        ]

        if total == None:
            raise ConflictError("total is None")

        return PaginatedResponse(
            items=validate_projects,
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size,
        )
