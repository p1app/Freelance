from sqlalchemy import select

from db.models import User
from db.database import async_session_maker
from db.enums import RoleEnum



class UserDAO():


    model=User

    async def create(email: str, username: str, hashed_password: str, role: RoleEnum, fullname: str, bio: str, skills: str):
        async with async_session_maker() as session:
            user = User(email=email, username=username, hashed_password=hashed_password, 
                        role=role, fullname=fullname, bio=bio, skills=skills)

            session.add(user)
            session.commit()
            session.refresh(user)

            return user

    async def get_by_id(cls, user_id: int):
            async with async_session_maker() as session:
                query = select(cls.model).where(cls.model.id == user_id)
                user = session.scalar(query)

                return user

    async def get_by_id(cls, user_email: int):
                async with async_session_maker() as session:
                    query = select(cls.model).where(cls.model.email == user_email)
                    user = session.scalar(query)
    
                    return user

    async def get_by_id(cls, user_username: int):
                async with async_session_maker() as session:
                    query = select(cls.model).where(cls.model.username == user_username)
                    user = session.scalar(query)
    
                    return user

    async def update(cls, user: UserUpdate):
                    async with async_session_maker() as session:
                        user = session.scalar(query)
        
                        return user

# update 

# delete ( is_active_false )

# list_users ( фильтр по роли,  пагинация )

# get_freelancers ( фильтр по навыкам, рейтингу )

# search_by_skills 

# block

# unblock