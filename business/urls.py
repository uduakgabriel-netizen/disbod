# business/urls.py

from django.urls import path
from .views import (
    BusinessListCreateView,
    BusinessDetailView,
    BusinessVerificationRequestCreateView,
    BusinessVerificationApproveView
)

urlpatterns = [
    path('', BusinessListCreateView.as_view(), name='business-list-create'),
    path('<int:pk>/', BusinessDetailView.as_view(), name='business-detail'),
    path('verify/request/', BusinessVerificationRequestCreateView.as_view(), name='business-verification-request'),
    path('verify/approve/<int:pk>/', BusinessVerificationApproveView.as_view(), name='business-verification-approve'),
]
