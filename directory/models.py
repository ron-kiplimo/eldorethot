from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Escort(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    city = models.CharField(max_length=100)
    services = models.TextField()
    rates = models.DecimalField(max_digits=10, decimal_places=2)
    availability = models.CharField(max_length=100, default="Not specified")
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    bio = models.TextField(default="No bio provided")
    phone_number = models.CharField(max_length=15)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Subscription(models.Model):
    escort = models.ForeignKey(Escort, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField()
    is_active = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.expiry_date:
            self.expiry_date = self.start_date + timezone.timedelta(days=30)
        super().save(*args, **kwargs)

    def check_status(self):
        if timezone.now() > self.expiry_date:
            self.is_active = False
            self.save()
        return self.is_active

    def __str__(self):
        return f"Subscription for {self.escort.name}"