import enum

class RoleEnum(str, enum.Enum):
    CLIENT = "client"
    FREELANCER = "freelancer"
    ADMIN = "admin"
