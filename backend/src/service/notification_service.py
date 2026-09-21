from core.exceptions import ConflictError, ForbiddenError, NotFoundError
from models.user_model import User as UserModel
from repository.notification_repo import NotificationRepository
from schemas.notification_schema import (
    NotificationCreateBase,
    NotificationCreateContract,
    NotificationCreateMessage,
    NotificationCreateMilestone,
    NotificationCreateProposal,
    NotificationCreateReview,
    NotificationResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession
from websocket.notifications_manager import ws_manager_notifications


class NotificationService:
    @classmethod
    async def create_for_contract(
        cls,
        session: AsyncSession,
        data: NotificationCreateContract
        | NotificationCreateMilestone
        | NotificationCreateMessage,
    ):
        notification = await NotificationRepository.create_for_contract(session, data)
        valid_data = NotificationResponse.model_validate(notification)
        await ws_manager_notifications.push(valid_data, valid_data.to_user_id)
        return valid_data

    @classmethod
    async def create_for_review(
        cls, session: AsyncSession, data: NotificationCreateReview
    ):
        notification = await NotificationRepository.create_for_review(session, data)
        valid_data = NotificationResponse.model_validate(notification)
        await ws_manager_notifications.push(valid_data, valid_data.to_user_id)
        return valid_data

    @classmethod
    async def create_for_proposal(
        cls, session: AsyncSession, data: NotificationCreateProposal
    ):
        notification = await NotificationRepository.create_for_proposal(session, data)

        return NotificationResponse.model_validate(notification)

    @classmethod
    async def create_for_system(
        cls, session: AsyncSession, data: NotificationCreateBase
    ):
        notification = await NotificationRepository.create_for_system(session, data)
        valid_data = NotificationResponse.model_validate(notification)
        await ws_manager_notifications.push(valid_data, valid_data.to_user_id)
        return valid_data

    @classmethod
    async def read_by_id(
        cls, session: AsyncSession, notification_id: int, current_user: UserModel
    ):
        notification = await NotificationRepository.read_by_id(session, notification_id)
        if notification is None:
            raise NotFoundError("notification not found")
        if notification.to_user_id != current_user.id:
            raise ForbiddenError("You can't read someone else's notification")
        return NotificationResponse.model_validate(notification)

    @classmethod
    async def read_all_by_user(cls, session: AsyncSession, current_user: UserModel):
        notifications = await NotificationRepository.read_all_by_user(
            session, current_user.id
        )
        if notifications is None:
            raise NotFoundError("notifications not found")
        validate_data = [NotificationResponse.model_validate(i) for i in notifications]
        return validate_data

    @classmethod
    async def get_list_by_user(
        cls, session: AsyncSession, current_user: UserModel
    ) -> list[NotificationResponse]:
        notifications = await NotificationRepository.get_list_by_user(
            session, current_user.id
        )
        if notifications is None:
            return []
        validate_data = [NotificationResponse.model_validate(i) for i in notifications]
        return validate_data

    @classmethod
    async def delete_by_id(
        cls, session: AsyncSession, notification_id: int, current_user: UserModel
    ):
        notification = await NotificationRepository.get_by_id(
            session=session, notification_id=notification_id
        )
        if notification is None:
            raise NotFoundError("notification not found")
        if notification.to_user_id != current_user.id:
            raise ForbiddenError("You can't delete someone else's notification")
        await NotificationRepository.delete_by_id(session, notification_id)
        return True

    @classmethod
    async def delete_all_by_user(cls, session: AsyncSession, current_user: UserModel):
        result = await NotificationRepository.delete_all_by_user(
            session, current_user.id
        )
        if result:
            return result
        else:
            raise ConflictError("error during notification deletion operation")
