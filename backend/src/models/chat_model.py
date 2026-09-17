from typing import TYPE_CHECKING

from core.database import Base
from sqlalchemy import Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

if TYPE_CHECKING:
    from models.contract_model import Contract  # noqa: TC004
    from models.user_model import User  # noqa: TC004


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    contract_id: Mapped[int] = mapped_column(
        ForeignKey("contracts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sender_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    message: Mapped[str] = mapped_column(Text, nullable=False)

    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Связи
    contract: Mapped[Contract] = relationship(
        "Contract",
        foreign_keys="ChatMessage.contract_id",
        back_populates="messages",
        lazy="selectin",
    )

    sender: Mapped[User] = relationship(
        "User",
        foreign_keys="ChatMessage.sender_id",
        back_populates="chat_messages",
        lazy="selectin",
    )

    @property
    def sender_name(self) -> str:
        return self.sender.fullname

    @validates("message")
    def validate_message(self, key: str, message: str) -> str:
        if not message or not message.strip():
            raise ValueError("сообщение не может быть пустым")
        return message
