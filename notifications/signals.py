from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from accounts.models import Follow
from chats.models import Message
from ratings.models import Rating
from .models import Notification

User = get_user_model()

# ✅ Notify when someone follows a user
@receiver(post_save, sender=Follow)
def send_follow_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            sender=instance.follower,
            receiver=instance.following,
            notification_type='follow',
            message=f"{instance.follower.username} started following you."
        )

# ✅ Notify when someone sends a message
@receiver(post_save, sender=Message)
def send_message_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            sender=instance.sender,
            receiver=instance.receiver,
            notification_type='message',
            message=f"New message from {instance.sender.username}: {instance.content[:40]}"
        )

# ✅ Notify when a user gets rated
@receiver(post_save, sender=Rating)
def send_rating_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            sender=instance.rater,
            receiver=instance.rated_user,
            notification_type='rating',
            message=f"{instance.rater.username} rated you {instance.stars} stars."
        )
