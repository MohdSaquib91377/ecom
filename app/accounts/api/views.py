from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegisterSerializer
from drf_yasg.utils import swagger_auto_schema
from otp.services import OTPManager, TwilioOTPService, Msg91OTPService


class UserRegisterView(APIView):
    @swagger_auto_schema(
        tags=["Accounts"],
        request_body=UserRegisterSerializer,
        operation_description="Register a new user",
        responses={201: 'User registered successfully', 400: 'Invalid request'}
    )
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_data = UserRegisterSerializer(user).data  # Serialize the saved user

           # Always send OTP if not verified
            if not user.is_mobile_verified:
                otp_manager = OTPManager(Msg91OTPService())
                otp = otp_manager.generate_and_send(user.mobile)
                print(f"OTP sent to {user.mobile}: {otp}")
            return Response(
                {"message": "User registered successfully", "data": user_data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
