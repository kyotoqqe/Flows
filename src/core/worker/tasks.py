import asyncio
import inspect
from aiosmtplib.errors import SMTPConnectError, SMTPTimeoutError, SMTPServerDisconnected

from src.mailing.service import SMTPConfirmationEmailSender
from src.core.worker.celery import app
from src.core.worker.exceptions import FunctionRealizationDontExist


SEND_EMAIL_REALIZATION = {
    "SMTPConfirmationEmailSender.send_email" : SMTPConfirmationEmailSender.send_email,
}

@app.task(
    name="mailing.tasks.send_email",
    ignore_result=True,
    autoretry_for=[
        SMTPConnectError,
        SMTPServerDisconnected,
        SMTPTimeoutError
    ],
    max_retries=5,
    retry_backoff=True,
    retry_jitter=True,
    soft_time_limit=30,
    asks_late=True,
    reject_on_worker_lost=True,
)
def send_email(
    realization_name:str,
    username: str,
    recipient: str,
    *args, **kwargs
):
    func = None
    print(args)
    for realization in SEND_EMAIL_REALIZATION.keys():
        if realization == realization_name:
            func = SEND_EMAIL_REALIZATION[realization]
            break

    if not func:
        raise FunctionRealizationDontExist

    if inspect.iscoroutinefunction(func):
        return asyncio.run(func(username, recipient, *args, **kwargs))
    
    return func(username, recipient, *args, **kwargs)


