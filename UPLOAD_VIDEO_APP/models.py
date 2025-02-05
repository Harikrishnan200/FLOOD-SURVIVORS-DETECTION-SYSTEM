from django.db import models
from AUTHENTICATION_APP.models import CustomUser  
from datetime import timedelta

class ProcessedVideo(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='processed_videos')
    video_name = models.CharField(max_length=255)
    output_video_path = models.CharField(max_length=255)
    total_persons_detected = models.IntegerField()
    processing_time = models.DurationField(
        default=timedelta(days=0, seconds=0, minutes=0), 
        null=True, 
        blank=True
    )
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    

    def __str__(self):
        return self.video_name