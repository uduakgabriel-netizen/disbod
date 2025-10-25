from rest_framework import generics, permissions
from .models import MediaFile
from mediafiles.serializers import MediaFileSerializer

class MediaFileListCreateView(generics.ListCreateAPIView):
    queryset = MediaFile.objects.all().order_by('-created_at')
    serializer_class = MediaFileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(uploader=self.request.user)
