from django.db import models
from datetime import date

class Child(models.Model):
    """
    A model representing a child with essential information such as their full name, 
    date of birth, gender, and any learning difficulties they may have. The child's 
    age is dynamically calculated based on their date of birth and is not stored 
    in the database.
    
    Attributes:
        name (str): The full name of the child.
        date_of_birth (date): The child's date of birth, used to calculate their age.
        gender (str): The gender of the child. Choices are 'male' or 'female'.
        learning_difficulty (str): The learning difficulty of the child, if applicable. Cannot be left blank or null.

    Methods:
        calculate_age(): Calculates the child's current age based on their date of birth.
        age (property): A property that returns the calculated age of the child.
        __str__(): Returns a string representation of the child (their full name).
    """
    
    # Choices for gender
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    
    # Fields
    name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    gender = models.CharField(
        max_length=6, 
        choices=GENDER_CHOICES, 
    )
    learning_difficulty = models.CharField(
        max_length=255, 
    )


    @property
    def age(self):
        """
        Returns the current age of the child. This is calculated by determining 
        the difference between today's date and the child's date of birth.
        
        Returns:
            int: The child's calculated age in years.
        """
        return self.calculate_age()

    def calculate_age(self):
        """
        Calculates the child's age based on their date of birth.
        The age is computed by subtracting the birth year from the current year, 
        and adjusting for whether the child's birthday has occurred yet this year.
        
        Returns:
            int: The child's calculated age in years.
        """
        today = date.today()
        age = today.year - self.date_of_birth.year
        # Adjust age if the current date is before the child's birthday this year
        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            age -= 1
        return age
    def __str__(self):
        """
        Returns the string representation of the child, which is their full name.
        
        Returns:
            str: The full name of the child.
        """
        return self.name

class Activity(models.Model):
    """
    Represents an educational activity designed for children.

    Attributes:
        activity_name (CharField): The name of the activity (e.g., "Touch the Correct Body Part").
        instruction (TextField): A detailed description of the steps involved in the activity.
    """
    
    activity_name = models.CharField(max_length=255)
    instruction = models.TextField()

    def __str__(self):
        """
        Returns the string representation of the Activity object, which is the activity's name.

        Returns:
            str: The name of the activity.
        """
        return self.activity_name