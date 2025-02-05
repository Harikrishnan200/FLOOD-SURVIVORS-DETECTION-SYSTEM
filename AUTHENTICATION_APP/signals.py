from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, UserToken

@receiver(post_save, sender=CustomUser)
def create_user_token(sender, instance, created, **kwargs):
    if created:
        UserToken.objects.create(user=instance)
