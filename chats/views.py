from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from accounts.models import User

class ConversationListView(generics.ListAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)


class StartConversationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        user = request.user
        receiver = get_object_or_404(User, id=user_id)

        # Check if conversation already exists
        conversation = Conversation.objects.filter(participants=user).filter(participants=receiver).first()
        if not conversation:
            conversation = Conversation.objects.create()
            conversation.participants.add(user, receiver)

        return Response(ConversationSerializer(conversation).data, status=status.HTTP_201_CREATED)


class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        conversation_id = self.kwargs['conversation_id']
        return Message.objects.filter(conversation_id=conversation_id)

    def perform_create(self, serializer):
        conversation = get_object_or_404(Conversation, id=self.kwargs['conversation_id'])
        receiver = [p for p in conversation.participants.all() if p != self.request.user][0]
        serializer.save(conversation=conversation, sender=self.request.user, receiver=receiver)
