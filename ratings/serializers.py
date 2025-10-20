from rest_framework import serializers
from .models import Rating
from accounts.models import User

class RatingSerializer(serializers.ModelSerializer):
    rater_username = serializers.CharField(source='rater.username', read_only=True)
    rated_username = serializers.CharField(source='rated_user.username', read_only=True)

    class Meta:
        model = Rating
        fields = [
            'id',
            'rater',
            'rater_username',
            'rated_user',
            'rated_username',
            'stars',
            'comment',
            'created_at'
        ]
        read_only_fields = ['rater', 'created_at']

    def validate_stars(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5 stars.")
        return value
