import asyncio
import signal

from sqlalchemy.orm import clear_mappers

from shared.infrastructure.ipc.messaging.adapters.rabbitmq.publisher import RabbitMQPublisher
from shared.infrastructure.ipc.messaging.ports.publisher import AbstractPublisher
from shared.infrastructure.outbox.adapters.sqlalchemy.processor import SQLAlchemyOutboxProcessor
from shared.infrastructure.outbox.ports.message import OutboxMessage, OutboxStatus
from shared.infrastructure.outbox.ports.processor import AbstractOutboxProcessor
# from shared.infrastructure.shared.sqlalchemy.connection import sessionmaker

MAX_RETRY_NUMBER = 5
MAX_BATCHES_COUNT = 5
SLEEP_TIME_IF_OUTBOX_IS_EMPTY = 10


class MessageProcessedError(Exception):
    def __init__(self, message_id):
        message = f"An error occurred while processing the message with id = {message_id}"
        super().__init__(message)
        self.message_id = message_id


class GracefulExit(SystemExit):
    pass


class EmptyBatch:
    pass


def shutdown():
    raise GracefulExit()


async def process_message(
    outbox: AbstractOutboxProcessor, outbox_message: OutboxMessage, publisher: AbstractPublisher
):
    print("here #1")
    try:
        message = {
            "message_id": str(outbox_message.event_id),
            "timestamp": outbox_message.timestamp,
            "type": outbox_message.type,
            "correlation_id": outbox_message.correlation_id,
            "body": outbox_message.payload,
        }
        await publisher.publish(message=message)
        print("good#1")
        await outbox.mark_message_as(message=outbox_message, status=OutboxStatus.processed)
        print("good#2")

    except Exception as e:
        print(f"Error {e}")
        raise MessageProcessedError(message_id=outbox_message.event_id)
    print("here#2")


async def retray_messages(
    outbox: AbstractOutboxProcessor, publisher: AbstractPublisher, messages_ids_for_retray: set
):
    messages_for_retray: list[OutboxMessage] = await outbox.get_messages_by_event_id(
        id_list=list(messages_ids_for_retray)
    )
    print(f"output {messages_for_retray}")
    for retray_message in messages_for_retray:
        message = {
            "message_id": str(retray_message.event_id),
            "timestamp": retray_message.timestamp,
            "type": retray_message.type,
            "correlation_id": retray_message.correlation_id,
            "body": retray_message.payload,
        }
        for i in range(MAX_RETRY_NUMBER):
            try:
                await publisher.publish(message=message)
                await outbox.mark_message_as(message=retray_message, status=OutboxStatus.processed)
                break
            except Exception:
                if i == MAX_RETRY_NUMBER - 1:
                    await outbox.mark_message_as(message=retray_message, status=OutboxStatus.failed)

        messages_ids_for_retray.discard(retray_message.event_id)


async def publish_outbox_batch(
    outbox: AbstractOutboxProcessor, publisher: AbstractPublisher, messages_ids_for_retray: set
):
    async with outbox:
        pending_messages = await outbox.get_pending_messages(10)

        if len(pending_messages) == 0:
            return EmptyBatch()

        for message in pending_messages:
            print(f"start process {message.event_id}")
            try:
                await process_message(outbox=outbox, outbox_message=message, publisher=publisher)
            except MessageProcessedError:
                messages_ids_for_retray.add(message.event_id)
        print("Batch done")


tasks = []
retray_tasks = set()


async def relay(outbox: AbstractOutboxProcessor, publisher: AbstractPublisher):
    messages_ids_for_retray = set()

    while True:
        for _ in range(MAX_BATCHES_COUNT):
            task = asyncio.create_task(
                publish_outbox_batch(
                    outbox=outbox,
                    publisher=publisher,
                    messages_ids_for_retray=messages_ids_for_retray,
                )
            )
            tasks.append(task)

        for finished_tasks in asyncio.as_completed(tasks):
            res = await finished_tasks
            if isinstance(res, EmptyBatch):
                print("sleep")
                await asyncio.sleep(SLEEP_TIME_IF_OUTBOX_IS_EMPTY)
        tasks.clear()

        if len(messages_ids_for_retray) > 0:
            retray_task = asyncio.create_task(
                retray_messages(
                    outbox=outbox,
                    publisher=publisher,
                    messages_ids_for_retray=messages_ids_for_retray,
                )
            )
            retray_tasks.add(retray_task)
            retray_task.add_done_callback(retray_tasks.discard)
            await asyncio.sleep(0)

        await asyncio.sleep(0.1)


async def gather_all_tasks():
    await asyncio.gather(*tasks)


async def main(outbox: AbstractOutboxProcessor, publisher: AbstractPublisher):

    async with publisher:
        await publisher.bootstrap()
        relay_task = asyncio.create_task(relay(outbox=outbox, publisher=publisher))
        await relay_task

    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGINT, shutdown)


# test all details together
"""
    if __name__ == "__main__":
    # mappers
    loop = asyncio.new_event_loop()

    try:
        outbox = SQLAlchemyOutboxProcessor(sessionmaker=sessionmaker)  # or your outbox
        publisher = RabbitMQPublisher()  # or your publisher
        loop.run_until_complete(main(outbox=outbox, publisher=publisher))
    except GracefulExit:
        loop.run_until_complete(gather_all_tasks())
    finally:
        clear_mappers()
        loop.close()
"""
