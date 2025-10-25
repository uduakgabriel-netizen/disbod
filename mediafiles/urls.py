from django.urls import path
from .views import MediaFileListCreateView

urlpatterns = [
    path('', MediaFileListCreateView.as_view(), name='mediafile-list-create'),
]
