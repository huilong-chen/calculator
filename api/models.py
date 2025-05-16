from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]
    
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    birth_date = models.DateField(null=True)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class LifestylePreferences(models.Model):
    FREQUENCY_CHOICES = [
        (1, 'Never'),
        (2, 'Rarely'),
        (3, 'Sometimes'),
        (4, 'Often'),
        (5, 'Very Often')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='lifestyle_preferences')
    
    # Smoking preferences
    smoking = models.IntegerField(choices=FREQUENCY_CHOICES, default=1)
    smoking_preference = models.IntegerField(choices=FREQUENCY_CHOICES, default=1)
    
    # Drinking preferences
    drinking = models.IntegerField(choices=FREQUENCY_CHOICES, default=1)
    drinking_preference = models.IntegerField(choices=FREQUENCY_CHOICES, default=1)
    
    # Exercise habits
    exercise = models.IntegerField(choices=FREQUENCY_CHOICES, default=3)
    exercise_preference = models.IntegerField(choices=FREQUENCY_CHOICES, default=3)
    
    # Work life balance (1-5 scale, 1=all work, 5=all life)
    work_life_balance = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=3
    )
    work_life_balance_preference = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=3
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Lifestyle preferences'

    def __str__(self):
        return f"{self.user.username}'s lifestyle preferences"

class Match(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_user2')
    compatibility_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user1', 'user2')
        
    def __str__(self):
        return f"Match between {self.user1.username} and {self.user2.username}"
