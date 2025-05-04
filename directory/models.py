from django.db import models
from django.contrib.auth.models import User

class Escort(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    city = models.CharField(max_length=100)
    services = models.TextField(help_text="Comma-separated list, e.g., massage, dinner dates")
    rates = models.CharField(max_length=100, help_text="Example: KES 5000/hr")
    availability = models.CharField(max_length=100, help_text="Example: Mon-Fri, 10am-10pm")
    profile_image = models.ImageField(upload_to='escort_images/', default='escort_images/default.jpg', null=True, blank=True)
    bio = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True, help_text="Enter a valid phone number, e.g., +254712345678")

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return round(sum(rating.value for rating in ratings) / ratings.count(), 1)
        return 0.0

class Rating(models.Model):
    escort = models.ForeignKey(Escort, related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('escort', 'user')