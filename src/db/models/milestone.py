from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from db.database import Base
from db.enums import MilestoneStatusEnum

if TYPE_CHECKING:
    from db.models.contract import Contract


class Milestone(Base):
    __tablename__ = "milestones"

    contract_id: Mapped[int] = mapped_column(
        ForeignKey("contracts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    due_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    status: Mapped[MilestoneStatusEnum] = mapped_column(
        default=MilestoneStatusEnum.PENDING,
        nullable=False,
    )

    # Связи
    contract: Mapped["Contract"] = relationship(
        "Contract",
        foreign_keys="Milestone.contract_id",
        back_populates="milestones",
        lazy="selectin",
    )

    @validates("due_date")
    def validate_due_date(self, key: str, due_date: datetime) -> datetime:
        if due_date < datetime.now():
            raise ValueError("due_date не может быть в прошлом")
        return due_date

    @validates("title")
    def validate_title(self, key: str, title: str) -> str:
        if not title or not title.strip():
            raise ValueError("title не может быть пустым")
        return title

    __table_args__ = (
        CheckConstraint(
            "due_date > CURRENT_TIMESTAMP",
            name="ck_milestone_due_date_future"
        ),
    )