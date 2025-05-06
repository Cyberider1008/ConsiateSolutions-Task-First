from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import ExpiringToken

class CustomAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token_key = request.headers.get('Authorization')

        if token_key:
            token_key = token_key.split(' ')[1]  # Assuming it's "Bearer <token>"
            try:
                token = ExpiringToken.objects.get(key=token_key)

                if token.is_expired():
                    raise AuthenticationFailed("Token has expired")

                # token.refresh()  # Refresh the token's expiration time

                return (token.user, token)  # Return the user and the token

            except ExpiringToken.DoesNotExist:
                raise AuthenticationFailed("Invalid token")

        return None
