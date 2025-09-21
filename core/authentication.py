from django.contrib.auth.models import User
from rest_framework import authentication, exceptions
from decouple import config

# Google ID token verification
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

class GoogleOIDCAuthentication(authentication.BaseAuthentication):
    """
    Custom DRF authentication that accepts Google's ID token in Authorization: Bearer <id_token>.
    It verifies the token against Google and returns (User, None).
    """

    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).decode('utf-8')
        if not auth_header:
            return None

        parts = auth_header.split()
        if parts[0].lower() != 'bearer' or len(parts) != 2:
            return None

        token = parts[1]
        client_id = config('GOOGLE_OIDC_CLIENT_ID', default=None)
        if not client_id:
            raise exceptions.AuthenticationFailed('Google OIDC client ID not configured')

        try:
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), client_id)
        except ValueError:
            raise exceptions.AuthenticationFailed('Invalid Google ID token')

        # idinfo contains fields like 'email', 'sub', 'name', 'given_name', 'family_name'
        email = idinfo.get('email')
        if not email:
            raise exceptions.AuthenticationFailed('No email in token')

        user, _ = User.objects.get_or_create(
            username=email,
            defaults={'email': email, 'first_name': idinfo.get('given_name', ''), 'last_name': idinfo.get('family_name', '')}
        )
        return (user, None)
