from db.models.project import Project
from db.database import async_session_maker
from schemas.project import ProjectCreate

from sqlalchemy import select

class ProjectDAO:

    model = Project

    @classmethod
    async def create(cls, data: ProjectCreate):
        with async_session_maker() as session:
            project = Project(title=data.title, description=data.description,
                              budget=data.budget, deadline=data.deadline, category=data.category)
            await session.add(project)
            await session.commit()