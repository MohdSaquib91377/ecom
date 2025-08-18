from rest_framework_simplejwt.tokens import RefreshToken


class JWTManager:
    def generate_tokens(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    