from rest_framework import serializers
from accounts.models import User

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "mobile"]

    def validate_mobile(self, value):
        """
        Custom validator for mobile numbers.
        Ensures exactly 10 digits.
        """
        print(f"Validating mobile number: {value}")
        
        mobile_str = str(value).strip()
        
        if not mobile_str.isdigit():
            raise serializers.ValidationError("Mobile number must contain only digits.")
        
        if len(mobile_str) != 10:
            raise serializers.ValidationError("Mobile number must be exactly 10 digits.")

        return mobile_str

    def create(self, validated_data):
        mobile = validated_data["mobile"]
        user = User.objects.filter(mobile=mobile).first()
        if user:
            if user.is_mobile_verified:
                raise serializers.ValidationError({"mobile": "Mobile number already exists."})
            return user  # return existing unverified user
        return User.objects.create(**validated_data)



class UpdateMobileSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)
    new_mobile = serializers.CharField(max_length=15)



class ProfileSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d %B %Y, %I:%M %p")

    class Meta:
        model = User
        fields = ["mobile", "created_at"]