from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from db.database import Base
from db.enums import ProposalStatusEnum

if TYPE_CHECKING:
    from db.models.contract import Contract
    from db.models.project import Project
    from db.models.user import User


class Proposal(Base):
    __tablename__ = "proposals"

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    freelancer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    contract_id: Mapped[int | None] = mapped_column(
        ForeignKey("contracts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    cover_letter: Mapped[str] = mapped_column(Text, nullable=False)
    bid_amount: Mapped[int] = mapped_column(nullable=False)
    estimated_days: Mapped[int] = mapped_column(nullable=False)

    status: Mapped[ProposalStatusEnum] = mapped_column(
        default=ProposalStatusEnum.PENDING,
        nullable=False,
        index=True,
    )

    # Связи
    project: Mapped["Project"] = relationship(
        "Project",
        foreign_keys="Proposal.project_id",
        back_populates="proposals",
        lazy="selectin",
    )

    freelancer: Mapped["User"] = relationship(
        "User",
        foreign_keys="Proposal.freelancer_id",
        back_populates="proposals",
        lazy="selectin",
    )

    contract: Mapped["Contract | None"] = relationship(
        "Contract",
        foreign_keys="Proposal.contract_id",
        back_populates="proposal",
        uselist=False,
        lazy="selectin",
    )

    @validates("freelancer_id")
    def validate_freelancer_id(self, key: str, freelancer_id: int) -> int:
        if freelancer_id == self.project.customer_id:
            raise ValueError(
                f"freelancer_id ({freelancer_id}) не может быть равен project.customer_id ({self.project.customer_id})"
            )
        return freelancer_id

    __table_args__ = (
        UniqueConstraint(
            "freelancer_id", "project_id",
            name="uq_proposal_freelancer_project"
        ),
    )