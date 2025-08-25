from rest_framework import serializers
from otp.models import OTP
from accounts.models import User

class SendOTPSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=10)


class VerifyOTPSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=10)
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        mobile = data["mobile"]
        otp_code = data["otp"]

        otp_obj = OTP.objects.filter(mobile=mobile, is_verified=False).order_by("-created_at").first()

        if not otp_obj:
            raise serializers.ValidationError({"otp": "No OTP found or already used"})

        if otp_obj.is_expired():
            raise serializers.ValidationError({"otp": "OTP expired"})

        if otp_obj.code != otp_code:
            raise serializers.ValidationError({"otp": "Invalid OTP"})

        otp_obj.is_verified = True
        otp_obj.save(update_fields=["is_verified"])
        # ✅ Mark User as mobile verified
        try:
            user = User.objects.get(mobile=mobile)
            user.is_mobile_verified = True
            user.save(update_fields=["is_mobile_verified"])
            data["user"] = user   # <--- Add user to validated_data

        except User.DoesNotExist:
            raise serializers.ValidationError({"mobile": "User not found"})

        return data
