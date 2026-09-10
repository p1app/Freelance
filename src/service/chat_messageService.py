from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import BusinessError, ForbiddenError, NotFoundError
from dao.ChatMessageDAO import ChatMessageDAO
from dao.ConractDAO import ContractDAO
from db.enums import ContractStatusEnum
from db.models.userModel import User as UserModel
from schemas.chat_messageSchema import (
    MessageCreate,
    MessageResponse,
    UnreadCountResponse,
)
from schemas.paginationSchema import PaginatedResponse


class ChatService:
    @classmethod
    async def send_message(
        cls,
        session: AsyncSession,
        current_user: UserModel,
        contract_id: int,
        data: MessageCreate,
    ) -> MessageResponse:
        contract = await ContractDAO.get_by_id(session=session, contract_id=contract_id)
        if contract is None:
            raise NotFoundError("Contract not found")

        if (
            current_user.id != contract.customer_id
            and current_user.id != contract.freelancer_id
        ):
            raise ForbiddenError("Only contract participants can send messages")

        if contract.status != ContractStatusEnum.ACTIVE:
            raise BusinessError("Cannot send messages to a non-active contract")

        if not data.message or not data.message.strip():
            raise BusinessError("Message cannot be empty")

        message = await ChatMessageDAO.create(
            session=session,
            message_data=data,
            contract_id=contract_id,
            sender_id=current_user.id,
        )

        return MessageResponse.model_validate(message)

    @classmethod
    async def get_messages(
        cls,
        session: AsyncSession,
        current_user: UserModel,
        contract_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse[MessageResponse]:
        contract = await ContractDAO.get_by_id(session=session, contract_id=contract_id)
        if contract is None:
            raise NotFoundError("Contract not found")

        if (
            current_user.id != contract.customer_id
            and current_user.id != contract.freelancer_id
        ):
            raise ForbiddenError("Only contract participants can view messages")

        messages, total = await ChatMessageDAO.get_by_contract(
            session=session,
            contract_id=contract_id,
            page=page,
            page_size=page_size,
        )

        await ChatMessageDAO.mark_all_as_read(
            session=session,
            contract_id=contract_id,
            user_id=current_user.id,
        )

        if not messages:
            return PaginatedResponse(
                items=[],
                total=0,
                page=page,
                page_size=page_size,
                pages=0,
            )

        validate_data = [
            MessageResponse.model_validate(message) for message in messages
        ]
        if total is None:
            total = 0
        return PaginatedResponse(
            items=validate_data,
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size,
        )

    @classmethod
    async def mark_as_read(
        cls,
        session: AsyncSession,
        current_user: UserModel,
        message_id: int,
    ) -> bool:
        message = await ChatMessageDAO.get_by_id(session=session, message_id=message_id)
        if message is None:
            raise NotFoundError("Message not found")

        if message.sender_id == current_user.id:
            raise BusinessError("You cannot mark your own message as read")

        contract = await ContractDAO.get_by_id(
            session=session, contract_id=message.contract_id
        )
        if contract is None:
            raise NotFoundError("Contract not found")

        if (
            current_user.id != contract.customer_id
            and current_user.id != contract.freelancer_id
        ):
            raise ForbiddenError("You do not have access to this message")

        result = await ChatMessageDAO.mark_as_read(
            session=session, message_id=message_id
        )
        if result is None:
            raise NotFoundError("Message not found")

        return result

    @classmethod
    async def mark_all_as_read(
        cls,
        session: AsyncSession,
        current_user: UserModel,
        contract_id: int,
    ) -> bool:
        contract = await ContractDAO.get_by_id(session=session, contract_id=contract_id)
        if contract is None:
            raise NotFoundError("Contract not found")

        if (
            current_user.id != contract.customer_id
            and current_user.id != contract.freelancer_id
        ):
            raise ForbiddenError("Only contract participants can mark messages as read")

        await ChatMessageDAO.mark_all_as_read(
            session=session,
            contract_id=contract_id,
            user_id=current_user.id,
        )

        return True

    @classmethod
    async def get_unread_count(
        cls,
        session: AsyncSession,
        current_user: UserModel,
        contract_id: int,
    ) -> UnreadCountResponse:
        contract = await ContractDAO.get_by_id(session=session, contract_id=contract_id)
        if contract is None:
            raise NotFoundError("Contract not found")

        if (
            current_user.id != contract.customer_id
            and current_user.id != contract.freelancer_id
        ):
            raise ForbiddenError("Only contract participants can view unread count")

        count = await ChatMessageDAO.get_unread_count(
            session=session,
            contract_id=contract_id,
            user_id=current_user.id,
        )

        return UnreadCountResponse(count=count)
