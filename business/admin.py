# business/admin.py

from django.contrib import admin
from .models import Business, BusinessVerificationRequest

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'category', 'is_verified', 'created_at')
    search_fields = ('name', 'owner__username', 'category')
    list_filter = ('is_verified', 'category')


@admin.register(BusinessVerificationRequest)
class BusinessVerificationRequestAdmin(admin.ModelAdmin):
    list_display = ('business', 'is_approved', 'reviewed_by', 'created_at')
    search_fields = ('business__name', 'reviewed_by__username')
    list_filter = ('is_approved',)
