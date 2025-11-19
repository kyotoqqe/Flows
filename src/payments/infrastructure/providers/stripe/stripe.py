import json
import decimal
import stripe


from src.payments.interfaces.providers import AbstractPaymentProvider
from src.payments.infrastructure.providers.stripe.config import stripe_settings

class StripePaymentProvider(AbstractPaymentProvider):
    stripe.api_key = stripe_settings.api_key    

    def create_checkout(self, price: decimal.Decimal, quantity: int, **kwargs):
        product = stripe.Price.create(
            currency="usd",
            unit_amount=1000,
            product_data={"name": "Organization"},
        )
        session = stripe.checkout.Session.create(
            line_items= [
                {
                    "price": product.id,
                    "quantity": quantity
                }
            ],
            mode="payment",
            payment_intent_data={"metadata": dict(**kwargs)},
            success_url=stripe_settings.success_url,
            cancel_url=stripe_settings.cancel_url
        )
        return session.url
    
    def get_payment_info(self, data, signature):
        event = None

        try:
            event = stripe.Event.construct_from(
                json.loads(data),
                signature, 
                stripe_settings.endpoint_secret)
        except stripe.SignatureVerificationError as e:
            print('⚠️  Webhook signature verification failed.' + str(e))
            return {"res": "error"}
        if event and event["type"] == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]["metadata"]
            print(type(payment_intent))
            print(payment_intent)
            payment_intent.pop("type")
            return payment_intent
        
