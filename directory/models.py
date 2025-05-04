from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Escort(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    age = models.IntegerField()
    rates = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.ImageField(upload_to='escort_images/', blank=True, null=True)
    average_rating = models.FloatField(default=0.0)
    # Added fields to match EscortForm
    services = models.TextField(blank=True, null=True)  # For listing services offered
    availability = models.CharField(max_length=100, blank=True, null=True)  # E.g., "Weekdays", "Weekends"
    bio = models.TextField(blank=True, null=True)  # Short biography

    def __str__(self):
        return self.name

class Subscription(models.Model):
    escort = models.ForeignKey(Escort, on_delete=models.CASCADE, related_name='subscriptions')
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=499.00)

    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = self.start_date + timezone.timedelta(days=30)
        super().save(*args, **kwargs)

    def check_status(self):
        now = timezone.now()
        if now > self.end_date:
            self.is_active = False
            self.save()
        return self.is_active

    def __str__(self):
        return f"Subscription for {self.escort.name} - Active: {self.is_active}"