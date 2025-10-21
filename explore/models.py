from django.db import models
from django.conf import settings
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class FeaturedBusiness(models.Model):
    """Admin-marked featured businesses for Explore frontpage."""
    business = models.OneToOneField('business.Business', on_delete=models.CASCADE, related_name='featured')
    promoted_until = models.DateTimeField(null=True, blank=True)
    note = models.CharField(max_length=255, blank=True)

    def is_active(self):
        return (self.promoted_until is None) or (self.promoted_until > timezone.now())

    def __str__(self):
        return f"Featured: {self.business.name}"


class TrendingProductCache(models.Model):
    """Cache structure for trending product calculations (optional)."""
    product = models.OneToOneField('products.Product', on_delete=models.CASCADE, related_name='trend_cache')
    score = models.FloatField(default=0.0)
    last_calculated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} (score={self.score:.2f})"
