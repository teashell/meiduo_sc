from django.contrib.auth.backends import ModelBackend
# from users.models import User
from users.models import User


class MyBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(username=username)
        except:
            try:
                user = User.objects.get(mobile=username)
            except:
                return None
        if user.check_password(password):
            return user
        else:
            return None
