from django.contrib import admin
from .models import Rating

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('rater', 'rated_user', 'stars', 'created_at')
    list_filter = ('stars', 'created_at')
    search_fields = ('rater__username', 'rated_user__username', 'comment')
