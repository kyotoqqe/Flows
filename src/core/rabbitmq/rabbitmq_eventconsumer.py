import asyncio

from src.core.database.orm import start_mappers as images_mappers
from src.auth.infrastructure.database.orm import start_mappers as users_mappers
from src.profiles.infrastructure.database.orm import start_mappers as profiles_mappers
from src.organizations.infrastructure.database.orm import start_mappers as organizations_mappers


from src.organizations.infrastructure.rabbitmq.broker import OrganizationRabbitMQBroker
from src.payments.infrastructure.rabbitmq.broker import PaymentsRabbitMQBroker

from src.core.rabbitmq.connection import get_connection

async def main():
    users_mappers()
    profiles_mappers()
    images_mappers()
    organizations_mappers()

    connection = await get_connection()

    async with connection:
        channel = await connection.channel()
        
        organization = OrganizationRabbitMQBroker()
        await organization.bootstrap(channel)

        payments = PaymentsRabbitMQBroker()
        await payments.bootstrap(channel)

        await asyncio.gather(
            organization.receive(channel),
            payments.receive(channel)
        )

        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())

