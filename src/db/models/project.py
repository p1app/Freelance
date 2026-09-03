from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from db.database import Base
from db.enums import ProjectCategoryEnum, ProjectStatusEnum

if TYPE_CHECKING:
    from db.models.user import User
    from db.models.proposal import Proposal
    from db.models.contract import Contract


class Project(Base):
    __tablename__ = "projects"

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(nullable=False)
    budget: Mapped[int] = mapped_column(nullable=False)
    deadline: Mapped[datetime] = mapped_column(nullable=False)
    category: Mapped[ProjectCategoryEnum] = mapped_column(nullable=False)

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )

    freelancer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )

    status: Mapped[ProjectStatusEnum] = mapped_column(
        default=ProjectStatusEnum.DRAFT, nullable=False, index=True
    )

    # Связи

    customer: Mapped["User"] = relationship(
        "User",
        foreign_keys="Project.customer_id",
        back_populates="projects_as_customer",
        lazy="selectin"
    )

    freelancer: Mapped["User | None"] = relationship(
        "User",
        foreign_keys="Project.freelancer_id",
        back_populates="projects_as_freelancer",
        lazy="selectin"
    )

    proposals: Mapped[list["Proposal"]] = relationship(
        "Proposal",
        foreign_keys="Proposal.project_id",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    contract: Mapped["Contract | None"] = relationship(
        "Contract",
        foreign_keys="Contract.project_id",
        back_populates="project",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="selectin"
    )

    # Валидация

    @validates("freelancer_id")
    def validate_freelance(self, key: str, freelancer_id: int | None) -> int | None:
        """Запрещает назначать исполнителя, если статус отличный от OPEN."""
        if freelancer_id is not None and self.status != ProjectStatusEnum.OPEN:
            raise ValueError(
                f"Нельзя выбрать исполнителя. Текущий статус проекта: '{self.status.value}' (ожидался 'open')."
            )
        return freelancer_id

    @validates("status")
    def validate_status(self, key: str, status: ProjectStatusEnum) -> ProjectStatusEnum:
        if status == ProjectStatusEnum.COMPLETED and self.freelancer_id is None:
            raise ValueError(
                f"Нельзя изменить статус на {ProjectStatusEnum.COMPLETED}. Необходимо выбрать исполнителя."
            )
        return status