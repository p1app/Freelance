from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base

if TYPE_CHECKING:
    from db.models.contract import Contract
    from db.models.user import User


class Review(Base):
    __tablename__ = "reviews"

    contract_id: Mapped[int] = mapped_column(
        ForeignKey("contracts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    from_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    to_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    rating: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Связи
    contract: Mapped["Contract"] = relationship(
        "Contract",
        foreign_keys="Review.contract_id",
        back_populates="reviews",
        lazy="selectin",
    )

    from_user: Mapped["User"] = relationship(
        "User",
        foreign_keys="Review.from_user_id",
        back_populates="reviews_from",
        lazy="selectin",
    )

    to_user: Mapped["User"] = relationship(
        "User",
        foreign_keys="Review.to_user_id",
        back_populates="reviews_to",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint(
            "contract_id", "from_user_id",
            name="uq_review_contract_from"
        ),
        CheckConstraint(
            "rating BETWEEN 1 AND 5",
            name="ck_review_rating_range"
        ),
    )