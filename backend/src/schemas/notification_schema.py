from datetime import datetime

from core.enums import NotificationTypeEnum
from pydantic import BaseModel, ConfigDict, model_validator


class NotificationCreateBase(BaseModel):
    type: NotificationTypeEnum
    to_user_id: int
    description: str


class NotificationCreateContract(NotificationCreateBase):
    contract_id: int

    @model_validator(mode="after")
    def check_type(self):
        if self.type != NotificationTypeEnum.CONTRACT:
            raise ValueError("Waiting type CONTRACT")
        return self


class NotificationCreateMilestone(NotificationCreateBase):
    contract_id: int

    @model_validator(mode="after")
    def check_type(self):
        if self.type != NotificationTypeEnum.MILESTONE:
            raise ValueError("Waiting type MILESTONE")
        return self


class NotificationCreateMessage(NotificationCreateBase):
    contract_id: int

    @model_validator(mode="after")
    def check_type(self):
        if self.type != NotificationTypeEnum.MESSAGE:
            raise ValueError("Waiting type MESSAGE")
        return self


class NotificationCreateReview(NotificationCreateBase):
    from_user_id: int

    @model_validator(mode="after")
    def check_type(self):
        if self.type != NotificationTypeEnum.REVIEW:
            raise ValueError("Waiting type REVIEW")
        return self


class NotificationCreateProposal(NotificationCreateBase):
    project_id: int

    @model_validator(mode="after")
    def check_type(self):
        if self.type != NotificationTypeEnum.PROPOSAL:
            raise ValueError("Waiting type PROPOSAL")
        return self


class NotificationResponse(BaseModel):
    id: int
    type: NotificationTypeEnum
    is_read: bool
    to_user_id: int
    description: str
    contract_id: (
        int | None  # для сообщения, создания контракта( принятия отклика ), этапов
    )
    from_user_id: int | None  # для отзыва
    project_id: int | None  # для отклика
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
