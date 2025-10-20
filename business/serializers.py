# business/serializers.py

from rest_framework import serializers
from .models import Business, BusinessVerificationRequest

class BusinessSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    is_verified = serializers.BooleanField(read_only=True)

    class Meta:
        model = Business
        fields = [
            'id', 'owner', 'name', 'description', 'category', 'logo',
            'phone_number', 'email', 'address', 'website', 'is_verified',
            'slug', 'created_at', 'updated_at'
        ]


class BusinessVerificationRequestSerializer(serializers.ModelSerializer):
    business_name = serializers.ReadOnlyField(source='business.name')
    reviewed_by_name = serializers.ReadOnlyField(source='reviewed_by.username')

    class Meta:
        model = BusinessVerificationRequest
        fields = [
            'id', 'business', 'business_name', 'message', 'is_approved',
            'reviewed_by', 'reviewed_by_name', 'created_at', 'updated_at'
        ]
