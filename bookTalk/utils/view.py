import jwt
from django.conf import settings


class BaseView:
    def get_user(self):
        token = self.request.headers.get('Authorization').split()[1]
        return jwt.decode(token, settings.SECRET_KEY,algorithms=['HS256'])['user_id']


