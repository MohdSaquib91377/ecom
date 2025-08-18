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
