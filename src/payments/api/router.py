from fastapi import APIRouter, Body, Request
from fastapi.responses import RedirectResponse

from src.core.messagebus import MessageBus
from src.payments.infrastructure.rabbitmq.broker import PaymentsRabbitMQBroker

from src.payments.api.schemas import Services
from src.payments.infrastructure.providers.stripe.stripe import StripePaymentProvider
from src.payments.application.events import OrganizationPaymentSucceeded

router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)


@router.post("/create_checkout_session")
async def create_checkout(checkout: Services = Body(discriminator="type")):
    stripe = StripePaymentProvider()
    checkout_url = stripe.create_checkout(**checkout.model_dump())
    return checkout_url

@router.post("/webhook")
async def webhook(request: Request):
    data = await request.body()
    signature = request.headers.get("stripe-signature")
    
    stripe = StripePaymentProvider()
    payment = stripe.get_payment_info(data, signature)

    if payment:
        messagebus = MessageBus(
            event_handlers={},
            command_handlers={},
            broker=PaymentsRabbitMQBroker()
        )

        event = OrganizationPaymentSucceeded(**payment)
        await messagebus.handle(event)