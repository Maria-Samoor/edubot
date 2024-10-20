from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import string

class IsEntireAlphaPasswordValidator:
    """
    Validator that checks if the password consists entirely of alphabetic characters.
    """
    def validate(self, password, user=None):
        """
        Validates the password to ensure it does not consist entirely of alphabetic characters.

        Args:
            password (str): The password to validate.
            user (UserProfile, optional): The user associated with the password. Defaults to None.

        Raises:
            ValidationError: If the password is entirely alphabetic.
        """
        if password.isalpha():
            raise ValidationError(
                _("Password cannot consist entirely of alphabetic characters."),
                code='password_entire_alpha',
            )

    def get_help_text(self):
        """
        Provides help text for the password validator.

        Returns:
            str: Help text for the password validation.
        """
        return _("Password cannot consist entirely of alphabetic characters.")

class HasUpperCasePasswordValidator:
    """
    Validator that checks if the password contains at least one uppercase letter.
    """
    def validate(self, password, user=None):
        """
        Validates the password to ensure it contains at least one uppercase letter.

        Args:
            password (str): The password to validate.
            user (UserProfile, optional): The user associated with the password. Defaults to None.

        Raises:
            ValidationError: If the password does not contain an uppercase letter.
        """
        if not any(char.isupper() for char in password):
            raise ValidationError(
                _("Password must contain at least one uppercase letter."),
                code='password_no_upper',
            )

    def get_help_text(self):
        """
        Provides help text for the password validator.

        Returns:
            str: Help text for the password validation.
        """
        return _("Password must contain at least one uppercase letter.")

class HasLowerCasePasswordValidator:
    """
    Validator that checks if the password contains at least one lowercase letter.
    """
    def validate(self, password, user=None):
        """
        Validates the password to ensure it contains at least one lowercase letter.

        Args:
            password (str): The password to validate.
            user (UserProfile, optional): The user associated with the password. Defaults to None.

        Raises:
            ValidationError: If the password does not contain a lowercase letter.
        """
        if not any(char.islower() for char in password):
            raise ValidationError(
                _("Password must contain at least one lowercase letter."),
                code='password_no_lower',
            )

    def get_help_text(self):
        """
        Provides help text for the password validator.

        Returns:
            str: Help text for the password validation.
        """
        return _("Password must contain at least one lowercase letter.")

class HasNumberPasswordValidator:
    """
    Validator that checks if the password contains at least one numeric character.
    """
    def validate(self, password, user=None):
        """
        Validates the password to ensure it contains at least one numeric character.

        Args:
            password (str): The password to validate.
            user (UserProfile, optional): The user associated with the password. Defaults to None.

        Raises:
            ValidationError: If the password does not contain a numeric character.
        """
        if not any(char.isdigit() for char in password):
            raise ValidationError(
                _("Password must contain at least one numeric character."),
                code='password_no_digit',
            )

    def get_help_text(self):
        """
        Provides help text for the password validator.

        Returns:
            str: Help text for the password validation.
        """
        return _("Password must contain at least one numeric character.")
    
class HasSpecialCharacterPasswordValidator:
    """
    Validator that checks if the password contains at least one special character.
    """
    def validate(self, password, user=None):
        """
        Validates the password to ensure it contains at least one special character.

        Args:
            password (str): The password to validate.
            user (UserProfile, optional): The user associated with the password. Defaults to None.

        Raises:
            ValidationError: If the password does not contain a special character.
        """
        special_characters = set(string.punctuation)
        if not any(char in special_characters for char in password):
            raise ValidationError(
                _("Password must contain at least one special character."),
                code='password_no_special_character',
            )

    def get_help_text(self):
        """
        Provides help text for the password validator.

        Returns:
            str: Help text for the password validation.
        """
        return _("Password must contain at least one special character.")