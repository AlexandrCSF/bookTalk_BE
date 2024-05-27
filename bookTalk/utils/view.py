from datetime import datetime

import jwt
from django.conf import settings
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken


class BaseView:
    def get_user(self):
        token = self.request.headers.get('Authorization').split()[1]
        return jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])['user_id']

    @staticmethod
    def update_token(user):
        refresh = RefreshToken.for_user(user)
        if user.refresh_token:
            old_token = OutstandingToken.objects.filter(token=user.refresh_token)
            if old_token:
                BlacklistedToken.objects.create(token=old_token.first())
                old_token.first().delete()
            if not OutstandingToken.objects.filter(token=refresh):
                OutstandingToken.objects.create(token=refresh, expires_at=datetime.now() + settings.SIMPLE_JWT[
                    'ACCESS_TOKEN_LIFETIME'])
        user.refresh_token = refresh
        user.save()
        return {
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user_id': user.id
        }
