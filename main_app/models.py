from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.core.validators import MinValueValidator

class EcoActivity(models.Model):
    CATEGORY_CHOICES = [
        ('ENERGY', 'Energy Consumption'),
        ('WATER', 'Water Usage'),
        ('WASTE', 'Waste Management'),
        ('TRANSPORT', 'Transportation'),
        ('RECYCLING', 'Recycling'),
    ]

    IMPACT_LEVELS = [
        ('LOW', 'Low Impact'),
        ('MEDIUM', 'Medium Impact'),
        ('HIGH', 'High Impact'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    value = models.FloatField(validators=[MinValueValidator(0.0)])
    unit = models.CharField(max_length=20)
    date = models.DateField(default=timezone.now)
    verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='verified_activities'
    )
    impact_level = models.CharField(
        max_length=10,
        choices=IMPACT_LEVELS,
        default='MEDIUM'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    location = models.CharField(max_length=255, blank=True)
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags")

    def __str__(self):
        return f"{self.user.username} - {self.category} ({self.value} {self.unit})"

    def get_absolute_url(self):
        return reverse('admin:main_app_ecoactivity_change', args=[self.id])

    class Meta:
        verbose_name_plural = "Eco Activities"
        ordering = ['-date']
        indexes = [
            models.Index(fields=['user', 'category', 'date']),
            models.Index(fields=['verified', 'impact_level']),
        ]

class SustainabilityGoal(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('OVERDUE', 'Overdue'),
    ]

    PRIORITY_CHOICES = [
        ('LOW', 'Low Priority'),
        ('MEDIUM', 'Medium Priority'),
        ('HIGH', 'High Priority'),
        ('URGENT', 'Urgent'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    target_value = models.FloatField(validators=[MinValueValidator(0.0)])
    current_value = models.FloatField(default=0, validators=[MinValueValidator(0.0)])
    unit = models.CharField(max_length=20)
    deadline = models.DateField()
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='PENDING'
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='MEDIUM'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    reminder_frequency = models.IntegerField(
        default=7,
        help_text="Reminder frequency in days"
    )
    last_reminder_sent = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    category = models.CharField(
        max_length=20,
        choices=EcoActivity.CATEGORY_CHOICES,
        default='ENERGY',
        help_text="Category this goal belongs to"
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_goals'
    )

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def get_absolute_url(self):
        return reverse('admin:main_app_sustainabilitygoal_change', args=[self.id])

    def get_progress_percentage(self):
        if self.target_value == 0:
            return 0
        return min(100, (self.current_value / self.target_value) * 100)

    def calculate_progress(self):
        """Calculate the progress percentage for this sustainability goal"""
        if self.target_value == 0:
            return 0
        
        current = self.current_value or 0
        target = self.target_value or 1  # Avoid division by zero
        progress = (current / target) * 100
        
        # Round to 1 decimal place
        return round(progress, 1)

    def is_overdue(self):
        return self.deadline < timezone.now().date() and self.status not in ['COMPLETED', 'CANCELLED']

    def save(self, *args, **kwargs):
        if self.is_overdue() and self.status not in ['COMPLETED', 'CANCELLED']:
            self.status = 'OVERDUE'
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['deadline']
        indexes = [
            models.Index(fields=['user', 'status', 'deadline']),
            models.Index(fields=['priority', 'category']),
        ]
