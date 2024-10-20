from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """
    Custom token generator class for account activation, extending Django's built-in PasswordResetTokenGenerator.
    It generates tokens used for securely activating user accounts via email verification.
    """
    def _make_hash_value(self, user, timestamp):
        """
        Generates a hash value to create a token for the user based on the user’s primary key (pk),
        the timestamp, and the user’s 'is_active' status.

        Args:
            user (User): The user object for which the token is being created.
            timestamp (int): A timestamp representing the time of token creation.

        Returns:
            str: A unique hash value that combines the user's primary key, timestamp, and active status.
        """
        return (
            six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.is_active)
        )

account_activation_token = AccountActivationTokenGenerator() # Create an instance of the AccountActivationTokenGenerator


class ResetPasswordTokenGenerator(PasswordResetTokenGenerator):
    """
    Custom token generator for resetting passwords.

    This class extends Django's built-in PasswordResetTokenGenerator and overrides
    the `_make_hash_value` method to generate a hash based on the user's primary key (pk),
    timestamp, and active status.

    The generated token is used to validate the password reset request and ensure the 
    reset process is secure.
    """

    def _make_hash_value(self, user, timestamp):
        """
        Generate a hash value for the password reset token.

        Args:
            user (User): The user for whom the token is being generated.
            timestamp (int): The timestamp when the token is generated.

        Returns:
            str: A unique string value used for hashing the token, combining the user's primary key,
                 the timestamp, and the user's active status.
        """
        return (
            six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.is_active)
        )

reset_password_token = ResetPasswordTokenGenerator() # Instantiate the token generator

