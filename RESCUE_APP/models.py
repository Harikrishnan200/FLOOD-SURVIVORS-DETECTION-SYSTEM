from django.db import models
from AUTHENTICATION_APP.models import CustomUser 

class RescueDetails(models.Model):
    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Completed", "Completed"),
    )
    latitude = models.FloatField()
    longitude = models.FloatField()
    location_name = models.CharField(max_length=100, blank=True, null=True)
    town_name = models.CharField(max_length=100, blank=True, null=True)
    detected_count = models.IntegerField(default=0)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='Pending')
    is_rescued = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='rescue_details') 

    def __str__(self):
        return f"{self.latitude}, {self.longitude}, {self.detected_count}, {self.status}, {self.is_rescued}"



class RescueTeam(models.Model):
    rescue_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='rescue_team')
    added_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='rescue_team_admin')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.rescue_user}, {self.added_by}"
