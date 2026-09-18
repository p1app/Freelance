from typing import TYPE_CHECKING

from core.database import Base
from core.enums import ProposalStatusEnum
from sqlalchemy import ForeignKey, Text, UniqueConstraint, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from models.contract_model import Contract  # noqa: TC004
    from models.project_model import Project  # noqa: TC004
    from models.user_model import User  # noqa: TC004


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

    cover_letter: Mapped[str] = mapped_column(Text, nullable=False)
    bid_amount: Mapped[DECIMAL] = mapped_column(nullable=False)
    estimated_days: Mapped[int] = mapped_column(nullable=False)

    status: Mapped[ProposalStatusEnum] = mapped_column(
        default=ProposalStatusEnum.PENDING,
        nullable=False,
        index=True,
    )

    # Связи
    project: Mapped[Project] = relationship(
        "Project",
        foreign_keys="Proposal.project_id",
        back_populates="proposals",
        lazy="selectin",
    )

    freelancer: Mapped[User] = relationship(
        "User",
        foreign_keys="Proposal.freelancer_id",
        back_populates="proposals",
        lazy="selectin",
    )

    contract: Mapped[Contract | None] = relationship(
        "Contract",
        foreign_keys="Contract.proposal_id",
        back_populates="proposal",
        uselist=False,
    )

    @property
    def freelancer_name(self) -> str:
        return self.freelancer.fullname

    __table_args__ = (
        UniqueConstraint(
            "freelancer_id", "project_id", name="uq_proposal_freelancer_project"
        ),
    )

    @property
    def project_title(self) -> str:
        return self.project.title
