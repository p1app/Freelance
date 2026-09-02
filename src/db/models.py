from sqlalchemy import ARRAY, Boolean, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import Base
from src.db.enums import RoleEnum


class User(Base):
    __tablename__ = "users"

    email: Mapped[String] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[String] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[String] = mapped_column(String(255))
    role: Mapped[RoleEnum] = mapped_column(
        default = RoleEnum.CLIENT, nullable=False
    )
    fullname: Mapped[String] = mapped_column(String(255), nullable=False)
    bio: Mapped[Text | None] = mapped_column(nullable=True)
    skills: Mapped[ARRAY | None] = mapped_column(ARRAY(String), nullable=True)
    raiting: Mapped[Float] = mapped_column(default=0)
    compeleted_projects: Mapped[Integer] = mapped_column(default=0)
    is_active: Mapped[Boolean] = mapped_column(default=True)