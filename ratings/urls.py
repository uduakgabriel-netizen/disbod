from django.urls import path
from . import views

urlpatterns = [
    path('', views.RatingListCreateView.as_view(), name='rating-list-create'),
    path('<int:pk>/', views.RatingDetailView.as_view(), name='rating-detail'),
]
