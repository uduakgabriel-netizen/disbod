from django.contrib import admin
from .models import FeaturedBusiness, TrendingProductCache

@admin.register(FeaturedBusiness)
class FeaturedBusinessAdmin(admin.ModelAdmin):
    list_display = ('business', 'promoted_until', 'note', 'is_active')
    search_fields = ('business__name', 'business__owner__username')
    list_filter = ('promoted_until',)


@admin.register(TrendingProductCache)
class TrendingProductCacheAdmin(admin.ModelAdmin):
    list_display = ('product', 'score', 'last_calculated')
    search_fields = ('product__name', 'product__category__name')
