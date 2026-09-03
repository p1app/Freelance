from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from db.database import Base
from db.enums import ContractStatusEnum

if TYPE_CHECKING:
    from db.models.chat_message import ChatMessage
    from db.models.milestone import Milestone
    from db.models.project import Project
    from db.models.proposal import Proposal
    from db.models.review import Review
    from db.models.user import User


class Contract(Base):
    __tablename__ = "contracts"

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    proposal_id: Mapped[int] = mapped_column(
        ForeignKey("proposals.id", ondelete="RESTRICT"),
        unique=True,
        nullable=False,
        index=True,
    )
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
    )
    freelancer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
    )

    final_price: Mapped[int] = mapped_column(nullable=False)

    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    end_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    status: Mapped[ContractStatusEnum] = mapped_column(
        default=ContractStatusEnum.ACTIVE,
        nullable=False,
    )

    # Связи
    project: Mapped["Project"] = relationship(
        "Project",
        foreign_keys="Contract.project_id",
        back_populates="contract",
        lazy="selectin",
    )

    proposal: Mapped["Proposal"] = relationship(
        "Proposal",
        foreign_keys="Contract.proposal_id",
        back_populates="contract",
        lazy="selectin",
    )

    customer: Mapped["User"] = relationship(
        "User",
        foreign_keys="Contract.customer_id",
        back_populates="contracts_as_customer",
        lazy="selectin",
    )

    freelancer: Mapped["User"] = relationship(
        "User",
        foreign_keys="Contract.freelancer_id",
        back_populates="contracts_as_freelancer",
        lazy="selectin",
    )

    reviews: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="contract",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="contract",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    milestones: Mapped[list["Milestone"]] = relationship(
        "Milestone",
        back_populates="contract",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @validates("customer_id", "freelancer_id")
    def validate_users(self, key: str, value: int) -> int:
        if key == "customer_id" and hasattr(self, "freelancer_id") and self.freelancer_id == value:
            raise ValueError("customer_id и freelancer_id должны быть разными")
        if key == "freelancer_id" and hasattr(self, "customer_id") and self.customer_id == value:
            raise ValueError("customer_id и freelancer_id должны быть разными")
        return value

    __table_args__ = (
        CheckConstraint(
            "final_price > 0",
            name="ck_contract_final_price_positive"
        ),
    )