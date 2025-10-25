from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import BusinessPost
from .serializers import BusinessPostSerializer

class BusinessPostListCreateView(generics.ListCreateAPIView):
    queryset = BusinessPost.objects.all().order_by('-created_at')
    serializer_class = BusinessPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class BusinessPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BusinessPost.objects.all()
    serializer_class = BusinessPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
