from rest_framework import serializers
from accounts.models import User
from business.models import Business
from products.models import Product, ProductCategory
from ratings.models import Rating
from explore.models import FeaturedBusiness

class MiniUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_image']

class BusinessListSerializer(serializers.ModelSerializer):
    owner = MiniUserSerializer(source='owner', read_only=True)
    average_rating = serializers.FloatField(source='owner.average_rating', read_only=True)
    followers_count = serializers.IntegerField(source='owner.followers_count', read_only=True)
    is_verified = serializers.BooleanField(source='is_verified', read_only=True)

    class Meta:
        model = Business
        fields = ['id', 'name', 'slug', 'category', 'logo', 'description',
                  'owner', 'average_rating', 'followers_count', 'country', 'region', 'city', 'is_verified']


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    business_name = serializers.ReadOnlyField(source='category.business.name')
    business_id = serializers.ReadOnlyField(source='category.business.id')

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'image', 'is_featured', 'stock',
                  'created_at', 'category', 'category_name', 'business_name', 'business_id']


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'description']
