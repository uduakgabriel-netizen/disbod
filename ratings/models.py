from django.db import models
from django.conf import settings
from django.db.models import Avg

User = settings.AUTH_USER_MODEL

class Rating(models.Model):
    rater = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_ratings')
    rated_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_ratings')
    stars = models.PositiveSmallIntegerField(default=1)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('rater', 'rated_user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.rater} rated {self.rated_user} ({self.stars}⭐)"

    def save(self, *args, **kwargs):
        """Save rating and auto-update rated user's average rating"""
        super().save(*args, **kwargs)
        self.update_user_average()

    def update_user_average(self):
        avg = Rating.objects.filter(rated_user=self.rated_user).aggregate(avg_stars=Avg('stars'))['avg_stars']
        self.rated_user.average_rating = avg or 0
        self.rated_user.save(update_fields=['average_rating'])
