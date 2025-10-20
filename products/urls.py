from django.urls import path
from . import views

urlpatterns = [
    # ✅ Product Categories
    path('categories/', views.ProductCategoryListCreateView.as_view(), name='category-list-create'),

    # ✅ Products
    path('products/', views.ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),

    # ✅ Product Views
    path('products/<int:pk>/view/', views.ProductViewRecordView.as_view(), name='product-view-record'),
    path('products/<int:pk>/views/', views.ProductViewListView.as_view(), name='product-view-list'),
]
