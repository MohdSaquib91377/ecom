from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from otp.models import OTP
from otp.api.serializers import SendOTPSerializer, VerifyOTPSerializer
from drf_yasg.utils import swagger_auto_schema
from otp.services import OTPManager, TwilioOTPService, Msg91OTPService
from tokens.services import JWTManager

class SendOTPView(APIView):
    @swagger_auto_schema(tags=["OTP"], request_body=SendOTPSerializer, operation_description="Send OTP", responses={201: 'OTP sent successfully', 400: 'Invalid request'})
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        if serializer.is_valid():
            mobile = serializer.validated_data["mobile"]

            # TODO: integrate with SMS provider (Twilio, MSG91, etc.)
            # For testing we return OTP in response (remove in production!)
            otp_manager = OTPManager(Msg91OTPService())
            otp = otp_manager.generate_and_send(mobile)
            print(f"OTP sent to {mobile}: {otp}")
            return Response(
                {"message": "OTP sent successfully","data":{"mobile":otp.mobile}},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    @swagger_auto_schema(tags=["OTP"], request_body=VerifyOTPSerializer, operation_description="Verify OTP", responses={200: 'OTP verified successfully', 400: 'Invalid OTP'})
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            jwt_manager = JWTManager()
            tokens = jwt_manager.generate_tokens(serializer.validated_data["user"])
            return Response({"message": "OTP verified successfully", "tokens": tokens}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
