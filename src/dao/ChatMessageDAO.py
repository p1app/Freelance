from sqlalchemy import select, func

from db.models import ChatMessage
from db.database import async_session_maker
from schemas.chat_message import MessageCreate


class ChatMessageDAO:
    model = ChatMessage

    @classmethod
    async def create(cls, message_data: MessageCreate, contract_id: int, sender_id: int):
        async with async_session_maker() as session:
            message = ChatMessage(
                **message_data.model_dump(),
                contract_id=contract_id,
                sender_id=sender_id,
                is_read=False,
            )
            session.add(message)
            await session.commit()
            await session.refresh(message)
            return message

    @classmethod
    async def get_by_contract(cls, contract_id: int, page: int = 1, page_size: int = 20):
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .where(cls.model.contract_id == contract_id)
                .order_by(cls.model.created_at.desc())
            )

            count_query = select(func.count()).where(cls.model.contract_id == contract_id)
            total = await session.scalar(count_query)

            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)

            result = await session.execute(query)
            messages = result.scalars().all()

            return messages, total

    @classmethod
    async def mark_as_read(cls, message_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.id == message_id)
            message = await session.scalar(query)

            if message is None:
                return None

            message.is_read = True
            await session.commit()
            return True

    @classmethod
    async def mark_all_as_read(cls, contract_id: int, user_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).where(
                cls.model.contract_id == contract_id,
                cls.model.sender_id != user_id,
                cls.model.is_read == False,
            )
            messages = await session.scalars(query)

            for message in messages:
                message.is_read = True

            await session.commit()

    @classmethod
    async def get_unread_count(cls, contract_id: int, user_id: int):
        async with async_session_maker() as session:
            query = select(func.count()).where(
                cls.model.contract_id == contract_id,
                cls.model.sender_id != user_id,
                cls.model.is_read == False,
            )
            return await session.scalar(query) or 0

    @classmethod
    async def get_last_message(cls, contract_id: int):
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .where(cls.model.contract_id == contract_id)
                .order_by(cls.model.created_at.desc())
                .limit(1)
            )
            return await session.scalar(query)

    @classmethod
    async def get_unread_by_user(cls, user_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).where(
                cls.model.sender_id != user_id,
                cls.model.is_read == False,
            )
            result = await session.execute(query)
            return result.scalars().all()