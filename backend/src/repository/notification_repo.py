from models.notification_model import Notification
from schemas.notification_schema import (
    NotificationCreateBase,
    NotificationCreateContract,
    NotificationCreateMessage,
    NotificationCreateMilestone,
    NotificationCreateProposal,
    NotificationCreateReview,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class NotificationRepository:
    model = Notification

    @classmethod
    async def create_for_contract(
        cls,
        session: AsyncSession,
        data: NotificationCreateContract
        | NotificationCreateMilestone
        | NotificationCreateMessage,
    ) -> Notification:
        notification = Notification(**data.model_dump(), is_read=False)
        session.add(notification)
        await session.commit()
        await session.refresh(notification)
        return notification

    @classmethod
    async def create_for_review(
        cls, session: AsyncSession, data: NotificationCreateReview
    ) -> Notification:
        notification = Notification(**data.model_dump(), is_read=False)
        session.add(notification)
        await session.commit()
        await session.refresh(notification)
        return notification

    @classmethod
    async def create_for_proposal(
        cls, session: AsyncSession, data: NotificationCreateProposal
    ):
        notification = Notification(**data.model_dump(), is_read=False)
        session.add(notification)
        await session.flush()
        await session.refresh(notification)
        return notification

    @classmethod
    async def create_for_system(
        cls, session: AsyncSession, data: NotificationCreateBase
    ):
        notification = Notification(**data.model_dump(), is_read=False)
        session.add(notification)
        await session.commit()
        await session.refresh(notification)
        return notification

    @classmethod
    async def get_by_id(cls, session: AsyncSession, notification_id: int):
        notification = await session.scalar(
            select(cls.model).where(cls.model.id == notification_id)
        )
        return notification

    @classmethod
    async def read_by_id(
        cls, session: AsyncSession, notification_id: int
    ) -> Notification | None:
        notification = await session.scalar(
            select(cls.model).where(cls.model.id == notification_id)
        )
        if notification:
            notification.is_read = True
            await session.commit()
            await session.refresh(notification)
        return notification

    @classmethod
    async def read_all_by_user(cls, session: AsyncSession, user_id: int):
        notifications = await cls.get_list_by_user(session=session, user_id=user_id)
        if notifications is None:
            return None
        for i in notifications:
            i.is_read = True
        await session.commit()
        for y in notifications:
            await session.refresh(y)
        return notifications

    @classmethod
    async def get_list_by_user(cls, session: AsyncSession, user_id: int):
        notifications = await session.execute(
            select(cls.model)
            .where(cls.model.to_user_id == user_id)
            .order_by(cls.model.created_at)
            .order_by(cls.model.id)
        )
        notifications = notifications.scalars().all()

        if len(notifications) == 0:
            return None

        return notifications

    @classmethod
    async def delete_by_id(cls, session: AsyncSession, notification_id: int):
        query = select(cls.model).where(cls.model.id == notification_id)
        notification = await session.scalar(query)
        if notification:
            await session.delete(notification)
            await session.commit()
            return True
        else:
            return False

    @classmethod
    async def delete_all_by_user(cls, session: AsyncSession, user_id: int):
        notifications = await cls.get_list_by_user(session, user_id)
        if notifications:
            for i in notifications:
                await session.delete(i)
            await session.commit()
            return True
        else:
            return False
