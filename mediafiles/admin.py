from django.contrib import admin
from .models import MediaFile

@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ('uploader', 'media_type', 'caption', 'created_at')
    list_filter = ('media_type',)
