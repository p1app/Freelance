from core.database import Base
from core.enums import NotificationTypeEnum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class Notification(Base):
    __tablename__ = "notifications"

    type: Mapped[NotificationTypeEnum] = mapped_column(nullable=False)
    to_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    description: Mapped[str]
    is_read: Mapped[bool] = mapped_column(default=False, nullable=False)
    contract_id: Mapped[int | None] = mapped_column(
        ForeignKey("contracts.id"), default=None, nullable=True
    )
    project_id: Mapped[int | None] = mapped_column(
        ForeignKey("projects.id"), default=None, nullable=True
    )
    from_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), default=None, nullable=True
    )
