from django import forms
from .models import Child
from datetime import date

class ChildForm(forms.ModelForm):
    """
    Form for handling the creation and validation of a Child model instance.
    This form is connected to the Child model and provides validation for 
    fields such as the child's name, date of birth, and gender.
    
    Attributes:
        Meta: 
            - model: Specifies that the form is based on the Child model.
            - fields: Specifies which fields from the Child model are included in the form.
            - widgets: Custom widgets for form fields (e.g., date input for date_of_birth).
    
    Methods:
        clean_date_of_birth(): Validates that the date of birth is before today's date.    
    """

    class Meta:
        model = Child
        fields = ['name', 'date_of_birth', 'gender', 'learning_difficulty']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_date_of_birth(self):
        """
        Custom validation for the date_of_birth field.
        
        Ensures that the provided date of birth is a past date, 
        meaning the child's date of birth must be earlier than today's date.
        
        Raises:
            ValidationError: If the date of birth is today or in the future.
        
        Returns:
            date: The validated date of birth.
        """
        dob = self.cleaned_data.get('date_of_birth')
        if dob >= date.today():
            raise forms.ValidationError("The date of birth cannot be today or a future date.")
        return dob
