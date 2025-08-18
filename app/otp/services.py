import requests
from twilio.rest import Client
from django.conf import settings
from otp.models import OTP


class OTPService:
    """Base OTP service interface."""
    def send(self, mobile: str, code: str):
        raise NotImplementedError("Subclasses must implement send()")


class Msg91OTPService(OTPService):
    """OTP service using MSG91."""
    def send(self, mobile: str, code: str):
        url = "https://api.msg91.com/api/v5/otp"
        payload = {
            "template_id": settings.MSG91_TEMPLATE_ID,
            "mobile": f"91{mobile}",
            "authkey": settings.MSG91_AUTH_KEY,
            "otp": code
        }
        requests.post(url, data=payload)


class TwilioOTPService(OTPService):
    """OTP service using Twilio."""
    def send(self, mobile: str, code: str):
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=f"Your OTP is {code}",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=f"+91{mobile}"
        )


class OTPManager:
    """Manager to handle OTP creation and sending."""
    def __init__(self, service: OTPService):
        self.service = service

    def generate_and_send(self, mobile: str):
        otp = OTP.objects.create(mobile=mobile)  # generate OTP in DB
        self.service.send(mobile, otp.code)
        return otp
