from django.db import models
from datetime import date, timedelta
from django.utils.timezone import now

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

class ChildActivity(models.Model):
    """
    A model representing a record of a child's performance in a specific educational activity.

    This model tracks the number of correct and incorrect answers provided by the child, 
    as well as the average time taken to complete the activity. Each child-activity 
    combination is unique, enforced by the `unique_together` constraint, ensuring that 
    each child has only one record per activity.

    Attributes:
        child (ForeignKey): A foreign key relationship to the `Child` model, representing 
            the child participating in the activity.
        activity (ForeignKey): A foreign key relationship to the `Activity` model, representing 
            the specific activity being tracked.
        correct_answers (IntegerField): The number of correct answers given by the child 
            for the activity. Defaults to 0.
        incorrect_answers (IntegerField): The number of incorrect answers given by the child 
            for the activity. Defaults to 0.
        start_activity (DateTimeField): The timestamp when the activity starts.
        stop_activity (DateTimeField): The timestamp when the activity ends.

    Methods:
        duration (property): A property that calculates the duration of the activity from the 
            start and stop timestamps.
        calculate_totals(): Calculates the total correct and incorrect answers from various stats.
        score (property): Returns the child's score for the activity based on the number of 
            correct and incorrect answers.
        __str__(): Returns a string representation of the record, displaying the child's name 
            and the activity name.
    
    Meta:
        unique_together (tuple): Ensures that each child can have only one unique record per 
            activity, preventing duplicate entries for the same child-activity pair.
    """
    
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    total_right_answers = models.IntegerField(default=0)
    total_wrong_answers = models.IntegerField(default=0)
    start_activity = models.DateTimeField(null=True, blank=True)
    stop_activity = models.DateTimeField(null=True, blank=True)

    class Meta:
        """
        Metadata for the ChildActivity model.

        unique_together (tuple): Ensures that each child can have only one unique record per 
            activity, preventing duplicate entries for the same child-activity pair.
        """
        unique_together = ('child', 'activity')

    def calculate_totals(self):
        """
        Calculates the total correct and incorrect answers based on the specific activity type.

        Depending on the activity, it queries relevant stats models like TouchBodyPartStats, 
        MatchColorStats, etc., to aggregate the data.
        """
        if self.activity.activity_name == "Touch Correct Body Part":
            stats = TouchBodyPartStats.objects.filter(child_activity=self)
        elif self.activity.activity_name == "Match the Color":
            stats = MatchColorStats.objects.filter(child_activity=self)
        elif self.activity.activity_name == "Finger Counting Game":
            stats = FindNumberStats.objects.filter(child_activity=self)
        elif self.activity.activity_name == "Find the Different Image":
            stats = FindImageStats.objects.filter(child_activity=self)
        elif self.activity.activity_name == "Learning with Buttons":
            stats = LearnWithButtonsStats.objects.filter(child_activity=self)
        else:
            return

        self.total_right_answers = sum(stat.right_answers for stat in stats)
        self.total_wrong_answers = sum(stat.wrong_answers for stat in stats)
        self.save()

    @property
    def duration(self):
        """
        Calculates the duration between the start and stop activity times.

        Returns:
            timedelta: The difference between stop_activity and start_activity.
        """
        if self.start_activity and self.stop_activity:
            duration_in_seconds = (self.stop_activity - self.start_activity).total_seconds()
            return round(duration_in_seconds / 60, 2)  # Convert to minutes and round to 2 decimal places
        return timedelta(0)
    
    @property
    def score(self):
        """
        Calculates the score for the child based on their correct and incorrect answers.

        The score can be calculated as a percentage of correct answers.

        Returns:
            float: The calculated score for the child in the activity. 
                    Returns 0 if there are no attempts.
        """
        if self.total_right_answers + self.total_wrong_answers > 0:
            return (self.total_right_answers / (self.total_right_answers + self.total_wrong_answers)) * 100
        return 0.0

    @property
    def level(self):
        score = self.score
        if score > 90:
            return "Excellent"
        elif 70 <= score <= 90:
            return "Good"
        elif 50 <= score < 70:
            return "Average"
        return "Needs Improvement"

    def __str__(self):
        """
        Returns a string representation of the ChildActivity object, 
        displaying the child's name and the activity name.

        Returns:
            str: A string in the format "Child Name - Activity Name".
        """
        return f"{self.child.name} - {self.activity.activity_name}"

class AttemptedModel(models.Model):
    """Base model to manage attempts."""
    attempt = models.PositiveIntegerField(default=1, editable=False)
    timestamp = models.DateTimeField(default=now, editable=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.pk:  # Only increment on new objects
            # Get the latest attempt number for this child_activity
            last_attempt = self.__class__.objects.filter(
                child_activity=self.child_activity
            ).order_by('-attempt').first()

            # Use the latest attempt number or start a new attempt group
            self.attempt = last_attempt.attempt if last_attempt else 1
            
            # Check if this is the first object in a new attempt group
            if self._is_new_attempt_group():
                self.attempt += 1 
            # Limit to the last 3 attempts (delete oldest if exceeding)
            if last_attempt and self.attempt > 3:
                oldest_attempt = self.__class__.objects.filter(
                    child_activity=self.child_activity, attempt=self.attempt - 3
                )
                oldest_attempt.delete()
        super().save(*args, **kwargs)
    def _is_new_attempt_group(self):
        """
        Determines whether a new attempt group should be started.
        Override this method in derived models if specific criteria apply.
        """
        return False  # Default behavior: continue the current attempt group
    
class TouchBodyPartStats(AttemptedModel):
    """
    Model to store statistics about the child’s interaction with different body parts (e.g., left hand, right hand, etc.)
    during an activity.

    Attributes:
        child_activity (ForeignKey): A reference to the `ChildActivity` model to link the stats to a specific activity.
        body_part (CharField): The body part being interacted with during the activity (e.g., 'left_hand', 'right_hand').
        right_answers (IntegerField): The number of correct answers provided by the child.
        wrong_answers (IntegerField): The number of incorrect answers provided by the child.
    
    Methods:
        score: Calculates the score as a percentage of correct answers out of the total attempts.
    """
    BODY_PART_CHOICES = [
        ('left_hand', 'Left Hand'),
        ('right_hand', 'Right Hand'),
        ('left_bumper', 'Left Bumper'),
        ('right_bumper', 'Right Bumper'),
    ]
    child_activity = models.ForeignKey(
        ChildActivity,
        on_delete=models.CASCADE,
        related_name="touch_body_part_stats"
        )
    body_part = models.CharField(max_length=20, choices=BODY_PART_CHOICES)
    right_answers = models.IntegerField(default=0)
    wrong_answers = models.IntegerField(default=0)

    class Meta:
        unique_together = ('child_activity','attempt', 'body_part')
    
    def _is_new_attempt_group(self):
        # Start a new attempt group if all body parts are already created for the latest attempt
        return self.__class__.objects.filter(
            child_activity=self.child_activity,
            attempt=self.attempt
        ).count() == len(self.BODY_PART_CHOICES)
    
    @property
    def score(self):
        """
        Calculates the score for the child based on their correct and incorrect answers.

        The score can be calculated as a percentage of correct answers.

        Returns:
            float: The calculated score for the child in the activity. 
                    Returns 0 if there are no attempts.
        """
        if self.right_answers + self.wrong_answers > 0:
            return (self.right_answers / (self.right_answers + self.wrong_answers)) * 100
        return 0.0
    
    @property
    def level(self):
        score = self.score
        if score > 90:
            return "Excellent"
        elif 70 <= score <= 90:
            return "Good"
        elif 50 <= score < 70:
            return "Average"
        return "Needs Improvement"
    
class MatchColorStats(AttemptedModel):
    """
    Model to store statistics about the child's interaction with color-matching activities.

    Attributes:
        child_activity (ForeignKey): A reference to the `ChildActivity` model to link the stats to a specific activity.
        color (CharField): The color the child interacted with (e.g., 'red', 'green').
        right_answers (IntegerField): The number of correct answers provided by the child.
        wrong_answers (IntegerField): The number of incorrect answers provided by the child.

    Methods:
        score: Calculates the score as a percentage of correct answers out of the total attempts.
    """
    COLOR_CHOICES = [
        ('red', 'Red'),
        ('yellow', 'Yellow'),
        ('green', 'Green'),
        ('blue', 'Blue'),
        ('black', 'Black'),
    ]
    child_activity = models.ForeignKey(
        ChildActivity,
        on_delete=models.CASCADE,
        related_name="match_color_stats"
        )    
    color = models.CharField(max_length=20, choices=COLOR_CHOICES)
    right_answers = models.IntegerField(default=0)
    wrong_answers = models.IntegerField(default=0)

    def _is_new_attempt_group(self):
        # Start a new attempt group if all body parts are already created for the latest attempt
        return self.__class__.objects.filter(
            child_activity=self.child_activity,
            attempt=self.attempt
        ).count() == len(self.COLOR_CHOICES)

    class Meta:
        unique_together = ('child_activity','attempt', 'color')
    
    @property
    def score(self):
        """
        Calculates the score for the child based on their correct and incorrect answers.

        The score can be calculated as a percentage of correct answers.

        Returns:
            float: The calculated score for the child in the activity. 
                    Returns 0 if there are no attempts.
        """
        if self.right_answers + self.wrong_answers > 0:
            return (self.right_answers / (self.right_answers + self.wrong_answers)) * 100
        return 0.0
    
    @property
    def level(self):
        score = self.score
        if score > 90:
            return "Excellent"
        elif 70 <= score <= 90:
            return "Good"
        elif 50 <= score < 70:
            return "Average"
        return "Needs Improvement"
    
class FindNumberStats(AttemptedModel):
    """
    Model to store statistics about the child's interaction with number recognition activities.

    Attributes:
        child_activity (ForeignKey): A reference to the `ChildActivity` model to link the stats to a specific activity.
        number (IntegerField): The number the child interacted with during the activity.
        right_answers (IntegerField): The number of correct answers provided by the child.
        wrong_answers (IntegerField): The number of incorrect answers provided by the child.

    Methods:
        score: Calculates the score as a percentage of correct answers out of the total attempts.
    """
    NUMBER_CHOICES = [
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('10', '10'),
    ]
    child_activity = models.ForeignKey(
        ChildActivity,
        on_delete=models.CASCADE,
        related_name="find_number_stats"
        )
    number = models.CharField(max_length=20, choices=NUMBER_CHOICES)
    right_answers = models.IntegerField(default=0)
    wrong_answers = models.IntegerField(default=0)

    class Meta:
        unique_together = ('child_activity','attempt', 'number')

    def _is_new_attempt_group(self):
        # Start a new attempt group if all body parts are already created for the latest attempt
        return self.__class__.objects.filter(
            child_activity=self.child_activity,
            attempt=self.attempt
        ).count() == len(self.NUMBER_CHOICES)
    
    @property
    def score(self):
        """
        Calculates the score for the child based on their correct and incorrect answers.

        The score can be calculated as a percentage of correct answers.

        Returns:
            float: The calculated score for the child in the activity. 
                    Returns 0 if there are no attempts.
        """
        if self.right_answers + self.wrong_answers > 0:
            return (self.right_answers / (self.right_answers + self.wrong_answers)) * 100
        return 0.0

    @property
    def level(self):
        score = self.score
        if score > 90:
            return "Excellent"
        elif 70 <= score <= 90:
            return "Good"
        elif 50 <= score < 70:
            return "Average"
        return "Needs Improvement"
    
class FindImageStats(AttemptedModel):
    """
    Model to store statistics about the child's interaction with image recognition activities.

    Attributes:
        child_activity (ForeignKey): A reference to the `ChildActivity` model to link the stats to a specific activity.
        image_type (CharField): The type of image the child interacted with (e.g., 'vegetable', 'fruit').
        right_answers (IntegerField): The number of correct answers provided by the child.
        wrong_answers (IntegerField): The number of incorrect answers provided by the child.

    Methods:
        score: Calculates the score as a percentage of correct answers out of the total attempts.
    """
    IMAGE_CHOICES = [
        ('fruits', 'Fruits'),
        ('shapes', 'Shapes'),
        ('vehicles', 'Vehicles'),
    ]
    child_activity = models.ForeignKey(
        ChildActivity,
        on_delete=models.CASCADE,
        related_name="find_image_stats"
        )
    image_type = models.CharField(max_length=20, choices=IMAGE_CHOICES)
    right_answers = models.IntegerField(default=0)
    wrong_answers = models.IntegerField(default=0)

    class Meta:
        unique_together = ('child_activity', 'attempt', 'image_type')  # Ensures one record per child_activity and image_type

    def _is_new_attempt_group(self):
        # Start a new attempt group if all body parts are already created for the latest attempt
        return self.__class__.objects.filter(
            child_activity=self.child_activity,
            attempt=self.attempt
        ).count() == len(self.IMAGE_CHOICES)
    
    @property
    def score(self):
        """
        Calculates the score for the child based on their correct and incorrect answers.

        The score can be calculated as a percentage of correct answers.

        Returns:
            float: The calculated score for the child in the activity. 
                    Returns 0 if there are no attempts.
        """
        if self.right_answers + self.wrong_answers > 0:
            return (self.right_answers / (self.right_answers + self.wrong_answers)) * 100
        return 0.0

    @property
    def level(self):
        score = self.score
        if score > 90:
            return "Excellent"
        elif 70 <= score <= 90:
            return "Good"
        elif 50 <= score < 70:
            return "Average"
        return "Needs Improvement"

class LearnWithButtonsStats(AttemptedModel):
    """
    Model to store statistics about the child's interaction with button press activities.

    Attributes:
        child_activity (ForeignKey): A reference to the `ChildActivity` model to link the stats to a specific activity.
        button (CharField): The button the child interacted with (e.g., 'horse', 'cat').
        right_answers (IntegerField): The number of correct answers provided by the child.
        wrong_answers (IntegerField): The number of incorrect answers provided by the child.

    Methods:
        score: Calculates the score as a percentage of correct answers out of the total attempts.
    """
    BUTTON_CHOICES = [
        ('horse', 'Horse'),
        ('cat', 'Cat'),
        ('dog', 'Dog'),
    ]
    child_activity = models.ForeignKey(
        ChildActivity,
        on_delete=models.CASCADE, 
        related_name="find_button_stats"
        )
    button = models.CharField(max_length=20, choices=BUTTON_CHOICES)
    right_answers = models.IntegerField(default=0)
    wrong_answers = models.IntegerField(default=0)

    class Meta:
        unique_together = ('child_activity','attempt', 'button')
    
    def _is_new_attempt_group(self):
        # Start a new attempt group if all body parts are already created for the latest attempt
        return self.__class__.objects.filter(
            child_activity=self.child_activity,
            attempt=self.attempt
        ).count() == len(self.BUTTON_CHOICES)
    
    @property
    def score(self):
        """
        Calculates the score for the child based on their correct and incorrect answers.

        The score can be calculated as a percentage of correct answers.

        Returns:
            float: The calculated score for the child in the activity. 
                    Returns 0 if there are no attempts.
        """
        if self.right_answers + self.wrong_answers > 0:
            return (self.right_answers / (self.right_answers + self.wrong_answers)) * 100
        return 0.0
    
    @property
    def level(self):
        score = self.score
        if score > 90:
            return "Excellent"
        elif 70 <= score <= 90:
            return "Good"
        elif 50 <= score < 70:
            return "Average"
        return "Needs Improvement"