from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MessageCreate(BaseModel):
    message: str = Field(min_length=1, max_length=5000)

class MessageResponse(BaseModel):
    id: int
    sender_id: int
    sender_name: str
    message: str
    is_read: bool
    created_at: datetime

    model_config=ConfigDict(from_attributes=True)

class UnreadCountResponse(BaseModel):
    count: int

    model_config=ConfigDict(from_attributes=True)