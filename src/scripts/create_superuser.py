import asyncio
from sqlalchemy.orm import clear_mappers

from src.core.domain.exceptions import EntityAlreadyExist

from src.auth.units_of_work import SQLAlchemyUsersUnitOfWork
from src.auth.domain.entities import User
from src.auth.domain.value_obj import UserRole
from src.auth.schemas import RegistrationSchema
from src.auth.infrastructure.utils import generated_password_hash
from src.auth.infrastructure.database.orm import start_mappers as user_mappers


async def create_superuser():
    email = input("Enter email: ")
    password = input("Enter password: ")
    password2 = input("Confirm password: ")
    
    try:
        RegistrationSchema(
            email=email,
            username="pupupu",
            password=password,
            password2=password2
        )
    except ValueError as e:
        print(str(e))
        confirm = input("Keep password ? Y/N: ")

        if confirm == "Y":
            pass
        else:
            raise ValueError("Failed to create superuser.")

    user_mappers()
    uow = SQLAlchemyUsersUnitOfWork()
    async with uow:
        user = await uow.users.get(email=email)

        if user:
            raise EntityAlreadyExist(
                    User,
                    email=email
                )
        
        password_hash = generated_password_hash(password=password)

        user = User(
            email=email,
            password=password_hash,
            role=UserRole.superuser,
            active=True
        )
        
        await uow.users.add(
            user,
            exclude = {"id", "created_at", "updated_at"}
        )
        await uow.commit()
        print("Successfully superuser creation!")
        clear_mappers()


if __name__ == '__main__':
    asyncio.run(create_superuser())