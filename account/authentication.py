from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model


User = get_user_model()

class EmailAuthenticationBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            if username:
                user = User.objects.get(email=username)
                if user.check_password(password):
                    return user
        except:
            return None
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except:
            return None
