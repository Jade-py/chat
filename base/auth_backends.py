from django.contrib.auth.backends import BaseBackend
from base.models import tblusers  # your custom user model

class PlainTextBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = tblusers.objects.get(code=username)
            if user.password == password:  # plain text comparison
                return user
        except tblusers.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return tblusers.objects.get(pk=user_id)
        except tblusers.DoesNotExist:
            return None
