# products/views.py

from rest_framework import generics, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import ProductCategory, Product, ProductView
from .serializers import ProductCategorySerializer, ProductSerializer, ProductViewSerializer


# ✅ CATEGORY LIST/CREATE VIEW
class ProductCategoryListCreateView(generics.ListCreateAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Automatically assign the logged-in user's business
        serializer.save(business=self.request.user)


# ✅ PRODUCT LIST/CREATE VIEW
class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all().select_related('category', 'category__business')
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['created_at', 'price']

    def perform_create(self, serializer):
        # Assign product to the selected category under the current user's business
        category = serializer.validated_data['category']
        if category.business != self.request.user:
            return Response({'error': 'You can only add products to your own category.'}, status=403)
        serializer.save()


# ✅ PRODUCT DETAIL VIEW (Retrieve, Update, Delete)
class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all().select_related('category', 'category__business')
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        product = self.get_object()
        if product.category.business != self.request.user:
            return Response({'error': 'You are not authorized to update this product.'}, status=403)
        serializer.save()

    def perform_destroy(self, instance):
        if instance.category.business != self.request.user:
            return Response({'error': 'You are not authorized to delete this product.'}, status=403)
        instance.delete()


# ✅ PRODUCT VIEW TRACKING (records when a user views a product)
class ProductViewRecordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        ProductView.objects.create(product=product, viewer=request.user)
        return Response({'message': f'View recorded for {product.name}'})


# ✅ PRODUCT VIEW LIST (to see who viewed what)
class ProductViewListView(generics.ListAPIView):
    serializer_class = ProductViewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        product_id = self.kwargs.get('pk')
        return ProductView.objects.filter(product_id=product_id).select_related('viewer', 'product')
