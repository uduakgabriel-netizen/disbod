from rest_framework import serializers
from .models import User
from .models import Follow

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "username", "email", "bio", "profile_image",
            "account_type", "business_name", "business_category",
            "business_subcategory", "location", "contact_number",
            "followers_count", "is_verified"
        ]
        read_only_fields = ["email", "followers_count", "is_verified"]



class FollowSerializer(serializers.ModelSerializer):
    follower_username = serializers.CharField(source='follower.username', read_only=True)
    following_username = serializers.CharField(source='following.username', read_only=True)

    class Meta:
        model = Follow
        fields = ["id", "follower", "follower_username", "following", "following_username", "created_at"]
        
        
class ExploreSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "username", "business_name", "account_type",
            "business_category", "country", "region", "city",
            "followers_count", "profile_image", "is_verified"
        ]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'business_name', 'profile_image', 'account_type']
        read_only_fields = ['id', 'username', 'business_name', 'profile_image', 'account_type']
        