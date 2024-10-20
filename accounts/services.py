from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from edubot.settings import EMAIL_HOST_USER
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib import messages
from .tokens import account_activation_token, reset_password_token

def send_activation_email(request, user, to_email):
    """
    Sends an activation email to the specified user.

    Args:
        request (HttpRequest): The HTTP request object.
        user (User): The user object for which the activation email is being sent.
        to_email (str): The recipient's email address.

    Sends an email with an activation link that the user can click to activate their account.
    The email includes a unique token and user identifier, encoded in a URL-safe format.
    A success or error message is displayed in the request's message queue depending on the result of the email sending.
    """
    mail_subject = 'Activate your user account.'
    message = render_to_string('accounts/registration/activate_account.html', {
        'user': user.full_name,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http',
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    
    if email.send():
        messages.success(request, f'Dear <b>{user}</b>, please go to your email <b>{to_email}</b> inbox and click on \
            the activation link to confirm your email. <b>Note:</b> Check your spam folder.')
    else:
        messages.error(request, f'Problem sending confirmation email to {to_email}, please check if the email is correct.')

def activate_user(uidb64, token):
    """
    Activates a user account if the provided token is valid.

    Args:
        uidb64 (str): The URL-safe base64 encoded user ID.
        token (str): The activation token to validate.

    Returns:
        User or None: Returns the activated user if successful; otherwise, returns None.

    This function decodes the user ID from the provided base64 string and retrieves the user object.
    If the user exists and the token is valid, the user is activated.
    Otherwise, it returns None.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user and account_activation_token.check_token(user, token):
        return user
    return None

def send_reset_email(request, user, to_email):
    """
    Sends a reset email to the specified user.

    Args:
        request (HttpRequest): The HTTP request object.
        user (User): The user object for which the reset email is being sent.
        to_email (str): The recipient's email address.

    Sends an email with an rest link that the user can click to reser their password.
    The email includes a unique token and user identifier, encoded in a URL-safe format.
    A success or error message is displayed in the request's message queue depending on the result of the email sending.
    """
    if user.is_active:
        mail_subject = 'Reset Your Password.'
        message = render_to_string('accounts/registration/reset_password.html', {
            'user': user.full_name,
            'domain': get_current_site(request).domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': reset_password_token.make_token(user),
            'protocol': 'https' if request.is_secure() else 'http'
        })

        email = EmailMessage(mail_subject, message, to=[to_email])
        if email.send():
            messages.success(request,f'Dear <b>{user}</b>, please go to you email <b>{to_email}</b> inbox and click on \
            the received Password Reset link to reset your password. <b>Note:</b> Check your spam folder.')
        else:
            messages.error(request, f'Problem sending confirmation email to {to_email}, check if you typed it correctly.')

def validate_reset_token(uidb64, token):
    """
    Validates the reset password token for a user.
    
    Args:
        uidb64 (str): URL-safe base64 encoded user ID.
        token (str): The token to validate.

    Returns:
        User or None: The user if the token is valid, None otherwise.
    """
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and reset_password_token.check_token(user, token):
        return user
    return None

def reset_user_password(user, new_password):
    """
    Resets the user's password to the new password provided.

    Args:
        user (User): The user object whose password will be reset.
        new_password (str): The new password to be set.

    Returns:
        bool: True if the password was successfully reset, False otherwise.
    """
    user.set_password(new_password)
    user.save()
    return True


def send_contactus_email(name, email, message):
    """
    Sends a notification email when a user submits a contact form.

    Args:
        name (str): The name of the person submitting the contact form.
        email (str): The email address of the person submitting the contact form.
        message (str): The message submitted by the user.

    Sends an email to the admin with the details of the contact form submission.
    """
    subject = 'New Contact Us Form Submission'
    message_body = f'Name: {name}\nEmail: {email}\nMessage: {message}'
    from_email = email  # Use the user's email as the sender
    recipient_list = [EMAIL_HOST_USER]  # Admin email or site email address to receive contact us submissions

    send_mail(subject, message_body, from_email, recipient_list)