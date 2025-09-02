from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,viewsets
from accounts.api.serializers import UserRegisterSerializer,ProfileSerializer,UpdateMobileSerializer,AddressSerializer
from drf_yasg.utils import swagger_auto_schema
from otp.services import OTPManager, TwilioOTPService, Msg91OTPService
from rest_framework.permissions import IsAuthenticated
from accounts.models import User,Address
from otp.models import OTP

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


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        tags=["Accounts"],
        operation_description="Get user profile",
        responses={200: 'Profile retrieved successfully', 400: 'Invalid request'}
    )
    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)



class UpdateMobileView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Accounts"],
        request_body=UpdateMobileSerializer,
        operation_description="Update mobile number",
        responses={200: 'Mobile number updated successfully', 400: 'Invalid request'}
    )
    def post(self, request):
        serializer = UpdateMobileSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user
            new_mobile = serializer.validated_data['new_mobile']
            otp = serializer.validated_data['otp']

            # --- Step 1: Get the latest OTP for the new mobile ---
            otp_obj = OTP.objects.filter(mobile=new_mobile, code=otp).order_by("-created_at").first()

            if not otp_obj:
                return Response(
                    {"error": "No OTP found for this mobile"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # --- Step 2: Check OTP expiration ---
            if otp_obj.is_expired():
                return Response(
                    {"error": "OTP has expired"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # --- Step 3: Check OTP validity ---
            if otp_obj.code != otp:
                return Response(
                    {"error": "Invalid OTP"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # --- Step 4: Check if mobile is already registered ---
            if User.objects.filter(mobile=new_mobile, is_mobile_verified=True).exists():
                return Response(
                    {"error": "This mobile is already registered with another account"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # --- Step 5: Update user's mobile ---
            user.mobile = new_mobile
            user.is_mobile_verified = True
            user.save()

            # --- Step 6: Mark OTP as verified ---
            otp_obj.is_verified = True
            otp_obj.save()

            return Response(
                {"message": "Mobile number updated successfully"},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users can only access their own addresses
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically assign the logged-in user
        serializer.save(user=self.request.user)
