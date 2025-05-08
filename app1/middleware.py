from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.utils import timezone

from .models import ExpiringToken
from datetime import timedelta

class ExpiringTokenMiddleware(MiddlewareMixin):

    def process_request(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Token '):
            return None  # or raise AuthenticationFailed

        token_key = auth_header.split(' ')[1]
        if not token_key:
            return None  # Let unauthenticated requests pass (or handle via views)

        try:
            token = ExpiringToken.objects.get(key=token_key)
        except ExpiringToken.DoesNotExist:
            return JsonResponse({"error": "Invalid token."}, status=401)

        if token.created + timedelta(minutes=1) < timezone.now():
            token.delete()
            return JsonResponse({"error": "Token expired."}, status=401)

        request.user = token.user
        request.auth = token
