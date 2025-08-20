from rest_framework import serializers
from accounts.models import User

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "mobile"]
        extra_kwargs = {
            "mobile": {"validators": []}  # disable default unique validator
        }

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