from django.contrib.auth.backends import ModelBackend
from .models import UserProfile
from django.db import models

class EmailOrFullNameBackend(ModelBackend):
    """
    Authentication backend that allows users to log in using either their email or full name.
    """
    def authenticate(self, request, username=None, password=None, **kwargs): 
        """
        Authenticates the user using their email or full name.

        Args:
            request (HttpRequest): The request object.
            username (str): The username (email or full name) to authenticate.
            password (str): The password to validate.
            **kwargs: Additional keyword arguments.

        Returns:
            UserProfile or None: The authenticated user or None if authentication fails.
        """
        try:
            user = UserProfile.objects.get(
                models.Q(full_name=username) | models.Q(email=username)
            )
        except UserProfile.DoesNotExist:
            return None
        if user.check_password(password):
            return user
        return None