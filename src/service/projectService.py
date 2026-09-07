from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from schemas.projectSchema import ProjectCreate, ProjectDetailResponse, ProjectListFilter, ProjectResponse, ProjectUpdate
from schemas.paginationSchema import PaginatedResponse

from core.exceptions import BusinessError, NotFoundError, ValidationError, ForbiddenError

from dao.ProjectDAO import ProjectDAO

from db.models.userModel import User as UserModel
from db.models.projectModel import Project as ProjectModel
from db.enums import ProjectStatusEnum, RoleEnum


def _check_ownership(project: ProjectModel, user_id: int):
    if project is None:
        raise NotFoundError("Project not found")
    if project.customer_id != user_id:
        raise ForbiddenError("You do not have ownership rights to this project")


class ProjectService:

    @classmethod
    async def create_project(cls, session: AsyncSession, data: ProjectCreate, customer_id: int) -> ProjectResponse:
        if data.deadline <= datetime.now():
            raise ValidationError("The deadline must not contain a time shorter than the present time")

        project = await ProjectDAO.create(session=session, project_data=data, customer_id=customer_id)

        return ProjectResponse.model_validate(project)

    @classmethod
    async def get_project(cls, session: AsyncSession, project_id: int) -> ProjectDetailResponse:
        project = await ProjectDAO.get_by_id(session=session, project_id=project_id)
        if project is None:
            raise NotFoundError("Project not found")
        
        response = ProjectDetailResponse.model_validate(project)
        response.proposal_count = len(project.proposals) if project.proposals else 0
        
        return response

    @classmethod
    async def update_project(cls, session: AsyncSession, project_id: int, data: ProjectUpdate, current_user: UserModel) -> ProjectResponse:
        project = await ProjectDAO.get_by_id(session=session, project_id=project_id)
        _check_ownership(project, current_user.id)

        if project.status != ProjectStatusEnum.DRAFT:
            raise BusinessError("The project cannot be changed to a status other than DRAFT")

        updated_project = await ProjectDAO.update(session=session, project_id=project_id, project_data=data)
        return ProjectResponse.model_validate(updated_project)

    @classmethod
    async def delete_project(cls, session: AsyncSession, current_user: UserModel, project_id: int) -> bool:
        project = await ProjectDAO.get_by_id(session=session, project_id=project_id)
        _check_ownership(project, current_user.id)

        if project.status not in [ProjectStatusEnum.DRAFT, ProjectStatusEnum.OPEN]:
            raise BusinessError("The project cannot be deleted with status other than DRAFT or OPEN")

        result = await ProjectDAO.delete(session=session, project_id=project_id)
        if result is None:
            raise NotFoundError("Project not found")
        return result

    @classmethod
    async def publish_project(cls, session: AsyncSession, current_user: UserModel, project_id: int) -> ProjectResponse:
        project = await ProjectDAO.get_by_id(session=session, project_id=project_id)
        _check_ownership(project, current_user.id)

        if project.status != ProjectStatusEnum.DRAFT:
            raise BusinessError("Only DRAFT projects can be published")

        published_project = await ProjectDAO.publish(session=session, project_id=project_id)
        return ProjectResponse.model_validate(published_project)

    @classmethod
    async def cancel_project(cls, session: AsyncSession, current_user: UserModel, project_id: int) -> ProjectResponse:
        project = await ProjectDAO.get_by_id(session=session, project_id=project_id)
        if project is None:
            raise NotFoundError("Project not found")

        if project.customer_id != current_user.id and current_user.role != RoleEnum.ADMIN:
            raise ForbiddenError("You do not have rights to cancel this project")

        if project.status not in [ProjectStatusEnum.OPEN, ProjectStatusEnum.IN_PROGRESS]:
            raise BusinessError("Only OPEN or IN_PROGRESS projects can be cancelled")

        cancelled_project = await ProjectDAO.cancel(session=session, project_id=project_id)
        return ProjectResponse.model_validate(cancelled_project)

    @classmethod
    async def assign_freelancer(cls, session: AsyncSession, current_user: UserModel, project_id: int, freelancer_id: int) -> ProjectResponse:
        project = await ProjectDAO.get_by_id(session=session, project_id=project_id)
        _check_ownership(project, current_user.id)

        if freelancer_id == current_user.id:
            raise BusinessError("The creator of the project cannot be its freelancer")

        updated_project = await ProjectDAO.assign_freelancer(session=session, project_id=project_id, freelancer_id=freelancer_id)
        return ProjectResponse.model_validate(updated_project)

    @classmethod
    async def list_projects(cls, session: AsyncSession, filters: ProjectListFilter, current_user: UserModel | None) -> PaginatedResponse[ProjectResponse]:
        if current_user is None:
            projects, total = await ProjectDAO.get_open_projects(session=session, page=filters.page, page_size=filters.page_size)
        else:
            projects, total = await ProjectDAO.list(session=session, data=filters)

        validate_projects = [
            ProjectResponse.model_validate(project)
            for project in projects
        ]

        return PaginatedResponse(
            items=validate_projects,
            total=total,
            page=filters.page,
            page_size=filters.page_size,
            pages=(total + filters.page_size - 1) // filters.page_size,
        )

    @classmethod
    async def get_my_projects(cls, session: AsyncSession, current_user: UserModel, page: int, page_size: int) -> PaginatedResponse[ProjectResponse]:
        projects, total = await ProjectDAO.get_by_customer(session=session, customer_id=current_user.id, page=page, page_size=page_size)

        validate_projects = [
            ProjectResponse.model_validate(project)
            for project in projects
        ]

        return PaginatedResponse(
            items=validate_projects,
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size,
        )

    @classmethod
    async def get_working_projects(cls, session: AsyncSession, current_user: UserModel, page: int, page_size: int) -> PaginatedResponse[ProjectResponse]:
        projects, total = await ProjectDAO.get_by_freelancer(session=session, freelancer_id=current_user.id, page=page, page_size=page_size)

        validate_projects = [
            ProjectResponse.model_validate(project)
            for project in projects
        ]

        return PaginatedResponse(
            items=validate_projects,
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size,
        )