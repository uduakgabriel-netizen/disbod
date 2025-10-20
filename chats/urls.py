from django.urls import path
from . import views

urlpatterns = [
    path('', views.ConversationListView.as_view(), name='conversation-list'),
    path('start/<int:user_id>/', views.StartConversationView.as_view(), name='start-conversation'),
    path('<int:conversation_id>/messages/', views.MessageListCreateView.as_view(), name='conversation-messages'),
]
