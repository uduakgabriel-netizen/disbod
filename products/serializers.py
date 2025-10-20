# products/serializers.py
from rest_framework import serializers
from .models import ProductCategory, Product, ProductView

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'business', 'name', 'description', 'created_at']
        read_only_fields = ['business', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    business = serializers.CharField(source='category.business.username', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'category_name', 'business', 'name', 'description',
            'price', 'image', 'is_featured', 'stock', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ProductViewSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    viewer_username = serializers.CharField(source='viewer.username', read_only=True)

    class Meta:
        model = ProductView
        fields = ['id', 'product', 'product_name', 'viewer', 'viewer_username', 'viewed_at']
        read_only_fields = ['viewed_at']
