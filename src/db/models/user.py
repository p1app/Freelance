from typing import TYPE_CHECKING

from sqlalchemy import ARRAY, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base
from db.enums import RoleEnum

if TYPE_CHECKING:
    from db.models.project import Project
    from db.models.proposal import Proposal
    from db.models.contract import Contract
    from db.models.review import Review
    from db.models.chat_message import ChatMessage


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[RoleEnum] = mapped_column(
        default = RoleEnum.CLIENT, nullable=False
    )

    fullname: Mapped[str] = mapped_column(String(255), nullable=False)
    bio: Mapped[str | None] = mapped_column(nullable=True)
    skills: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    raiting: Mapped[float] = mapped_column(default=0)
    compeleted_projects: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(default=True)

    # Проекты, где пользователь — заказчик
    projects_as_customer: Mapped[list["Project"]] = relationship(
        "Project",
        foreign_keys="Project.customer_id",
        back_populates="customer",
        lazy="selectin",
    )

    # Проекты, где пользователь — исполнитель
    projects_as_freelancer: Mapped[list["Project"]] = relationship(
        "Project",
        foreign_keys="Project.freelancer_id",
        back_populates="freelancer",
        lazy="selectin",
    )

    # Отклики пользователя (как фрилансер)
    proposals: Mapped[list["Proposal"]] = relationship(
        "Proposal",
        foreign_keys="Proposal.freelancer_id",
        back_populates="freelancer",
        lazy="selectin",
    )

    # Контракты, где пользователь — заказчик
    contracts_as_customer: Mapped[list["Contract"]] = relationship(
        "Contract",
        foreign_keys="Contract.customer_id",
        back_populates="customer",
        lazy="selectin",
    )

    # Контракты, где пользователь — исполнитель
    contracts_as_freelancer: Mapped[list["Contract"]] = relationship(
        "Contract",
        foreign_keys="Contract.freelancer_id",
        back_populates="freelancer",
        lazy="selectin",
    )

    # Отзывы, которые пользователь оставил
    reviews_from: Mapped[list["Review"]] = relationship(
        "Review",
        foreign_keys="Review.from_user_id",
        back_populates="from_user",
        lazy="selectin",
    )

    # Отзывы, которые пользователь получил
    reviews_to: Mapped[list["Review"]] = relationship(
        "Review",
        foreign_keys="Review.to_user_id",
        back_populates="to_user",
        lazy="selectin",
    )

    # Сообщения, которые пользователь отправил
    chat_messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage",
        foreign_keys="ChatMessage.sender_id",
        back_populates="sender",
        lazy="selectin",
    )