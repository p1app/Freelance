from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from db.database import Base

if TYPE_CHECKING:
    from db.models.contract import Contract
    from db.models.user import User


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
    contract: Mapped["Contract"] = relationship(
        "Contract",
        foreign_keys="ChatMessage.contract_id",
        back_populates="messages",
        lazy="selectin",
    )

    sender: Mapped["User"] = relationship(
        "User",
        foreign_keys="ChatMessage.sender_id",
        back_populates="chat_messages",
        lazy="selectin",
    )

    @validates("message")
    def validate_message(self, key: str, message: str) -> str:
        if not message or not message.strip():
            raise ValueError("сообщение не может быть пустым")
        return message