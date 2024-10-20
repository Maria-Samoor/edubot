from django.db import models
from django.contrib.auth.models import AbstractUser

class EmployeeID(models.Model):
    """
    Model representing an employee ID.
    """
    # Field for storing a unique employee ID, which can have a maximum length of 9 characters.
    employee_id = models.CharField(max_length=9, unique=True)

    def __str__(self):
        """
        Returns the string representation of the EmployeeID.

        Returns:
            str: The employee ID.
        """
        return self.employee_id

class UserProfile(AbstractUser):
    """
    User profile model extending the AbstractUser model to include additional fields.
    """
    # Field for storing the full name of the user. It is unique, meaning no two users can have the same name.
    full_name = models.CharField(max_length=255, unique=True)
    
    # Field for storing the user's email address. It must be unique to avoid duplicates.
    email = models.EmailField(unique=True)

    # Foreign key relationship to EmployeeID. If an EmployeeID is deleted, the corresponding UserProfile will also be deleted.
    # This field can be null or left blank if not applicable.
    employee_id = models.ForeignKey(EmployeeID, on_delete=models.CASCADE, null=True, blank=True , to_field='employee_id')

    # Override the default username field to use 'full_name' instead.
    username = None
    # Override the first_name field, not used in this custom user model.
    first_name = None
    # Override the last_name field, not used in this custom user model.
    last_name = None

    # Specify 'full_name' as the field to be used for authentication.
    USERNAME_FIELD = 'full_name'
    # Specify additional required fields during user creation. 'email' is included.
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        """
        Returns the string representation of the UserProfile.

        Returns:
            str: The full name of the user.
        """
        return self.full_name
    
class ContactUs(models.Model):
    """
    Model for storing contact messages from users.
    """
    # Field for the name of the contact person. It has a maximum length of 100 characters.
    name = models.CharField(max_length=100)
    
    # Field for storing the email address of the contact person.
    email = models.EmailField()
    
    # Field for storing the message sent by the user. It can hold a large amount of text.
    message = models.TextField()
    
    # Automatically set the creation time of the message when it is first created.
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns the string representation of the ContactUs message.

        Returns:
            str: The name of the contact.
        """
        return self.name