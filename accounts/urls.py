from django.urls import path,include
from .views import home,login,signup,faq,contactus,forgetpassword, activate, reset_password

"""
    URL configuration for the accounts application.

    Each entry in urlpatterns is mapped to a view from the views module.
    The name parameter assigns a unique name for each URL pattern, 
    which can be referenced in templates and other parts of the project.

    URL Patterns:
    - Home: Renders the home page of the site.
    - Login: Renders the login page for user authentication.
    - Signup: Renders the signup page for new user registration.
    - FAQ: Renders the FAQ page.
    - Contact Us: Renders the contact us page.
    - Forget Password: Renders the forget password page.
    - Activate: Activates a user account based on the provided UID and token.
    - Reset Password: Reset user password based on the provided UID and token.

    Args:
        request: HTTP request object.

    Returns:
        HttpResponse: Rendered template for each view function.
    """    
urlpatterns = [
    path('', home, name='home'), # Home page
    path('login/', login, name='login'), # Login page
    path('signup/', signup, name='signup'), # Signup page
    path('faq/', faq, name='faq'), # FAQ page
    path('contactus/', contactus, name='contactus'), # Contact Us page
    path('forgetpassword/', forgetpassword, name='forgetpassword'), # Forget Password page
    path('activate/<uidb64>/<token>', activate, name='activate'), # Activate User Account
    path('passwordreset/<uidb64>/<token>', reset_password, name='passwordreset'), # Reset User Password

]