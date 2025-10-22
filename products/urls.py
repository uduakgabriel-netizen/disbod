from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductListCreateView.as_view(), name='product-list-create'),
    path('categories/', views.ProductCategoryListCreateView.as_view(), name='category-list-create'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('products/<int:pk>/view/', views.ProductViewRecordView.as_view(), name='product-view-record'),
    path('products/<int:pk>/views/', views.ProductViewListView.as_view(), name='product-view-list'),
]
