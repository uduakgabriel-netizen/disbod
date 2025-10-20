from rest_framework import serializers
from .models import Notification
from accounts.models import User

class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_image']

class NotificationSerializer(serializers.ModelSerializer):
    sender = UserMiniSerializer(read_only=True)
    receiver = UserMiniSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'sender', 'receiver', 'notification_type',
            'message', 'related_object_id', 'is_read', 'created_at'
        ]
