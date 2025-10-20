from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='notifications'),
    path('<int:pk>/read/', views.MarkNotificationAsReadView.as_view(), name='mark-notification-read'),
    path('clear/', views.ClearNotificationsView.as_view(), name='clear-notifications'),
]
