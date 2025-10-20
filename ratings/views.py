from rest_framework import generics, permissions
from .models import Rating
from .serializers import RatingSerializer

# ✅ Create and List Ratings
class RatingListCreateView(generics.ListCreateAPIView):
    queryset = Rating.objects.all().select_related('rater', 'rated_user')
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(rater=self.request.user)

    def get_queryset(self):
        rated_user_id = self.request.query_params.get('rated_user')
        if rated_user_id:
            return self.queryset.filter(rated_user_id=rated_user_id)
        return self.queryset


# ✅ Retrieve, Update, Delete Specific Rating
class RatingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        rating = self.get_object()
        if rating.rater != self.request.user:
            raise PermissionError("You cannot edit someone else's rating.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.rater != self.request.user:
            raise PermissionError("You cannot delete someone else's rating.")
        instance.delete()
