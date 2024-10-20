from .services import send_activation_email, activate_user, send_contactus_email, send_reset_email, validate_reset_token
from django.contrib import messages
from .forms import SignUpForm, ContactUsForm, ForgotPasswordForm, PasswordResetForm, LoginForm
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from .models import ContactUs
from django.contrib.auth import authenticate 
from django.contrib.auth import login as auth_login

def home(request):
    """
    View for the home page of the application.
    
    Renders the home page template located at 'accounts/home.html'.
    
    Args:
        request: The HTTP request object.
    
    Returns:
        HttpResponse: Rendered home page template.
    """
    return render(request, 'accounts/home.html')

def faq(request):
    """
    View for the FAQ page.
    
    Renders the FAQ page template located at 'accounts/faq.html'.
    
    Args:
        request: The HTTP request object.
    
    Returns:
        HttpResponse: Rendered FAQ page template.
    """
    return render(request, 'accounts/faq.html')

def login(request):
    """
    View for the login page.
    
    Renders the login page template located at 'accounts/registration/login.html'.
    
    Handles both GET and POST requests:
    - On GET: Displays an empty login form.
    - On POST: Validates and processes the login form. If valid, authenticates the user and logs them in.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered login page template or redirects to the home page upon successful login.
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)  # Create a form instance with POST data

        if form.is_valid():
            # Authentication logic
            username_or_email = form.cleaned_data['email_or_username']  # Retrieve input from form
            password = form.cleaned_data['password']  # Retrieve password from form
            user = authenticate(request, username=username_or_email, password=password)  # Authenticate user
            
            if user is not None:
                auth_login(request, user)  # Log the user in
                return redirect('homepage')  # Redirect to home page after successful login
            else:
                 messages.error(request,'Invalid login credentials') # Add error for invalid credentials

    else:
        form = LoginForm()  # Initialize an empty login form on GET request

    return render(request, 'accounts/registration/login.html', {'form': form})  # Render the login page

def signup(request):
    """
    View for the signup page.
    
    Renders the signup page template located at 'accounts/registration/signup.html'.
    
    Handles both GET and POST requests:
    - On GET: Displays an empty signup form.
    - On POST: Validates and processes the signup form. If valid, creates a new user, sends an activation email, and redirects to the login page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered signup page template or redirects to the login page.
    """
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Set user as inactive until email confirmation
            user.save()
            send_activation_email(request, user, form.cleaned_data.get('email'))
            return redirect(reverse('login'))  # Redirect to login page after signup
    else:
        form = SignUpForm()  # Initialize an empty form on GET request
    
    return render(request, 'accounts/registration/signup.html', {'form': form})  # Render the signup page


def activate(request, uidb64, token):
    """
    Activates the user account after clicking on the email activation link.
    
    Validates the provided user ID and token. If valid, activates the user account.
    Displays appropriate messages based on the activation status.

    Args:
        request (HttpRequest): The HTTP request object.
        uidb64 (str): The URL-safe base64 encoded user ID.
        token (str): The activation token to validate.

    Returns:
        HttpResponse: Redirects to the login page after activation attempt.
    """
    user = activate_user(uidb64, token)  # Validate token and get user
    
    if user:
        if user.is_active:
            messages.error(request, 'Account is already activated. Please try logging in.')
        else:
            user.is_active = True  # Activate user account
            user.save()
            messages.success(request, f'Dear <b>{user}</b>, Thank you for your email confirmation. Now you can log in to your account.')
    else:
        messages.error(request, 'Activation link is invalid or expired. Please check your email or contact support.')

    return redirect('login')  # Redirect to login page

def forgetpassword(request):
    """
    View for the forget password page.
    
    Renders the forget password page template located at 'accounts/registration/forgetpassword.html'.
    
    Args:
        request: The HTTP request object.
    
    Returns:
        HttpResponse: Rendered forget password page template.
    """
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            User = get_user_model()
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, "This email address is not associated with any account.")
                return render(request, 'accounts/registration/forgetpassword.html', {'form': form})

            if not user.is_active:
                messages.error(request, "This account is not active.")
                return render(request, 'accounts/registration/forgetpassword.html', {'form': form})
            
            send_reset_email(request, user, email)
            return redirect(reverse('login'))  
    else:
        form = ForgotPasswordForm()

    return render(request, 'accounts/registration/forgetpassword.html', {'form': form})

def reset_password(request, uidb64, token):
    """
    Handles the password reset process by validating the token and resetting the user's password.

    Args:
        request (HttpRequest): The HTTP request object.
        uidb64 (str): URL-safe base64 encoded user ID.
        token (str): The password reset token.
    """
    user = validate_reset_token(uidb64, token)

    if user is not None:
        if request.method == 'POST':
            form = PasswordResetForm(request.POST)
            if form.is_valid():
                # Set the password using set_password to ensure it's properly hashed
                user.set_password(form.cleaned_data['password1'])
                user.save()

                messages.success(request, "Password reset successfully. You can now log in with your new password.")
                return redirect(reverse('login'))  # Redirect to a success page or login page
            else:
                for error in form.non_field_errors():
                    messages.error(request, error)
        else:
            form = PasswordResetForm()
        return render(request, 'accounts/registration/passwordreset.html', {'form': form, 'reset_error': None})
    else:
        messages.error(request, 'Invalid password reset link. Please request a new one.')
        form = PasswordResetForm()  
        return render(request, 'accounts/registration/login.html', {'form': form, 'reset_error': 'Invalid password reset link. Please request a new one.'})
    


def contactus(request):
    """
    Handles the submission of the Contact Us form. It saves the form data to the database and sends a notification email.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the 'contactus.html' template with the form, or redirects on success.
    """
    if request.method == 'POST':
        form = ContactUsForm(request.POST)
        if form.is_valid():
            ContactUs.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                message=form.cleaned_data['message'],
                created_at=timezone.now()
            )
            send_contactus_email(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                message=form.cleaned_data['message']
            )

            messages.success(request, "Thank you for contacting us! We will get back to you soon.")
            return redirect('login') 
    else:
        form = ContactUsForm() 

    return render(request, 'accounts/contactus.html', {'form': form})


