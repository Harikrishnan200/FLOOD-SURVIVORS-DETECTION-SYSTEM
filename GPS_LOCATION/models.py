from django.db import models


class Location(models.Model):
    STATUS_CHOICES = (
        ('Completed', 'Completed'),
        ('Pending', 'Pending'),
    )
    email = models.EmailField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    detected_count = models.IntegerField(default=0)
    is_first_location = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    is_detected = models.BooleanField(default=False)
    is_send = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.latitude}, {self.longitude} at {self.timestamp}"