from django import forms
from django.contrib.auth.forms import UserCreationForm,PasswordResetForm
from .models import UserProfile
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from .validators import (
    IsEntireAlphaPasswordValidator,
    HasUpperCasePasswordValidator,
    HasLowerCasePasswordValidator,
    HasNumberPasswordValidator,
    HasSpecialCharacterPasswordValidator,
)

class SignUpForm(UserCreationForm):
    """
    Custom form for user sign-up, extending Django's built-in UserCreationForm.
    This form handles validation for user information including full name, email, employee ID, and password.
    """
    
    class Meta:
        """
        Meta class defines the form’s model and the fields to be included in the form.
        - model: The UserProfile model, which stores the user's data.
        - fields: The fields that will be shown on the form ('full_name', 'email', 'employee_id', 'password1', 'password2').
        """
        model = UserProfile
        fields = ['full_name', 'email', 'employee_id', 'password1', 'password2']

    def clean_full_name(self):
        """
        Custom validation for the 'full_name' field.
        Ensures the full name contains only alphabetic characters or spaces.
        
        Returns:
            str: Cleaned full name if valid.
        
        Raises:
            ValidationError: If the full name contains non-alphabetic characters.
        """
        full_name = self.cleaned_data['full_name']
        if not all(char.isalpha() or char.isspace() for char in full_name):
            raise ValidationError('Full name must contain only letters and spaces.')
        return full_name

    def clean_employee_id(self):
        """
        Custom validation for the 'employee_id' field.
        Ensures the employee ID is exactly 9 digits and unique.
        
        Returns:
            str: Cleaned employee ID if valid.
        
        Raises:
            ValidationError: If the employee ID is not 9 digits or is already registered.
        """
        employee_id = self.cleaned_data.get('employee_id')
        if employee_id is not None:
            if len(str(employee_id)) != 9 or not str(employee_id).isdigit():
                raise ValidationError('Employee ID must be a 9-digit positive number.')
            if UserProfile.objects.filter(employee_id=employee_id).exists():
                raise ValidationError("This Employee ID is already registered.")
        return employee_id

    def clean_password1(self):
        """
        Custom validation for the 'password1' field (the first password input).
        Validates the password against custom validators: checking for alphabetical-only characters,
        uppercase, lowercase, numbers, and special characters.
        
        Returns:
            str: Cleaned password if valid.
        
        Raises:
            ValidationError: If the password does not meet validation criteria.
        """
        password = self.cleaned_data.get('password1')
        validators = [
            IsEntireAlphaPasswordValidator(),
            HasUpperCasePasswordValidator(),
            HasLowerCasePasswordValidator(),
            HasNumberPasswordValidator(),
            HasSpecialCharacterPasswordValidator(),
        ]

        for validator in validators:
            validator.validate(password)
        
        return password  # Return the validated password

    def clean_email(self):
        """
        Custom validation for the 'email' field.
        Ensures the email is unique within the UserProfile model.
        
        Returns:
            str: Cleaned email if valid.
        
        Raises:
            ValidationError: If the email is already registered.
        """
        email = self.cleaned_data.get('email')
        if UserProfile.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def clean(self):
        """
        Final clean method to validate the form as a whole.
        Checks that both password fields match.
        
        Returns:
            dict: Cleaned data from the form.
        
        Adds error:
            If passwords do not match, an error is added to the 'password2' field.
        """
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        # Check if passwords match
        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Passwords do not match.')  # Use add_error to associate the error with password2

        return cleaned_data
    
class ForgotPasswordForm(PasswordResetForm):
    """
    A custom form for users to request a password reset.
    This form extends Django's built-in PasswordResetForm and performs additional validation 
    to ensure the email address is associated with an existing user account and that the account is active.
    """
    email = forms.EmailField(label='Enter your email to reset password', max_length=254)
    def clean_email(self):
        """
        Cleans and validates the email field to ensure that the email is associated with an active user account.
        
        Raises:
            ValidationError: If the email is not associated with any account or if the account is inactive.
        
        Returns:
            str: The cleaned email address.
        """
        email = self.cleaned_data['email']
        User = get_user_model()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError("This email address is not associated with any account .")

        if not user.is_active:
            raise forms.ValidationError("Account not active or other validation issue.")

        return email

class PasswordResetForm(forms.Form):
    """
    A custom form for users to reset password .
    This form extends Django's built-in Form and performs additional validation 
    """
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean_password1(self):
        """
        Custom validation for the 'password1' field (the first password input).
        Validates the password against custom validators: checking for alphabetical-only characters,
        uppercase, lowercase, numbers, and special characters.
        
        Returns:
            str: Cleaned password if valid.
        
        Raises:
            ValidationError: If the password does not meet validation criteria.
        """
        password = self.cleaned_data.get('password1')
        validators = [
            IsEntireAlphaPasswordValidator(),
            HasUpperCasePasswordValidator(),
            HasLowerCasePasswordValidator(),
            HasNumberPasswordValidator(),
            HasSpecialCharacterPasswordValidator(),
        ]

        for validator in validators:
            validator.validate(password)
        
        return password  # Return the validated password

    def clean(self):
        """
        Final clean method to validate the form as a whole.
        Checks that both password fields match.
        
        Returns:
            dict: Cleaned data from the form.
        
        Adds error:
            If passwords do not match, an error is added to the 'password2' field.
        """
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        # Check if passwords match
        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Passwords do not match.')  # Use add_error to associate the error with password2

        return cleaned_data
    
class LoginForm(forms.Form):
    """
    Custom login form allowing users to sign in via email or username.
    Includes password and captcha validation.

    Attributes:
        email_or_username (CharField): A field for the user to enter their email address or username.
        password (CharField): A field for the user to enter their password, rendered as a password input.
        captcha (ReCaptchaField): A field for captcha validation to prevent automated logins.
    """
    
    email_or_username = forms.CharField(label=_('Email or Username'))  # Field for email or username input
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput)  # Field for password input, hidden characters
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)  # Captcha field for validation

    def __init__(self, *args, **kwargs):
        """
        Initialize the form and optionally pass the request object.

        Args:
            *args: Variable length argument list.
            **kwargs: Keyword arguments including an optional request object.
        """
        self.request = kwargs.pop('request', None)  # Store the request object for use in validation
        super().__init__(*args, **kwargs)  # Call the parent class's initializer

    def clean(self):
        """
        Perform form-wide validation, including checking if the user exists 
        and is active based on the email or username.

        Returns:
            dict: Cleaned data containing validated form fields.

        Raises:
            ValidationError: If the credentials are invalid or if the account is inactive.
        """
        cleaned_data = super().clean()  # Retrieve cleaned data from the parent class
        email_or_username = cleaned_data.get('email_or_username')  # Get user input for email or username
        password = cleaned_data.get('password')  # Get user input for password

        # If either field is empty, Django's built-in validation will handle this
        if not email_or_username or not password:
            return cleaned_data

        # Query the UserProfile model to find a matching user
        user = UserProfile.objects.filter(
            Q(full_name__iexact=email_or_username) | Q(email__iexact=email_or_username)
        ).first()  # Fetch the first matching user

        if not user:
            raise ValidationError('Invalid credentials. Please try again.')  # Raise error if user does not exist

        if not user.is_active:
            raise ValidationError('This account is inactive.')  # Raise error if user account is inactive

        return cleaned_data  # Return the cleaned data if all checks pass

    def clean_captcha(self):
        """
        Validate the captcha field to ensure it's filled out correctly.

        Returns:
            str: The validated captcha value.

        Raises:
            ValidationError: If the captcha validation fails.
        """
        captcha_value = self.cleaned_data.get('captcha')  # Get the value of the captcha field
        if not captcha_value:
            raise ValidationError('Captcha validation failed. Please try again.')  # Raise error if captcha is not valid
        return captcha_value  # Return the validated captcha value

class ContactUsForm(forms.Form):
    """
    A form for users to submit a contact request, including their name, email, and message.

    Fields:
        - name (str): The name of the person submitting the contact form. Max length 100 characters.
        - email (str): The email address of the person submitting the contact form.
        - message (str): The message submitted by the user.
    """
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)