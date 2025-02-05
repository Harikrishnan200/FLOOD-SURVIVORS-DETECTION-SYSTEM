from django.db import models


class Location(models.Model):
    email = models.EmailField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.latitude}, {self.longitude} at {self.timestamp}"