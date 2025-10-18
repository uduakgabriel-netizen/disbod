# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, EmailVerificationCode, UserRating, Follow

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Disbod Fields', {
            'fields': ('account_type', 'is_email_verified', 'profile_picture', 'phone_number',
                       'country', 'region', 'city', 'business_name', 'business_type', 'sub_category',
                       'verification_badge', 'is_suspended')
        }),
    )
    list_display = ('username', 'email', 'account_type', 'is_email_verified', 'verification_badge', 'is_suspended')
    search_fields = ('username', 'email', 'business_name')

@admin.register(EmailVerificationCode)
class EmailVerificationCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at', 'is_used')
    search_fields = ('user__email', 'code')

@admin.register(UserRating)
class UserRatingAdmin(admin.ModelAdmin):
    list_display = ('rated_user', 'rated_by', 'rating', 'created_at')
    search_fields = ('rated_user__username', 'rated_by__username')

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    search_fields = ('follower__username', 'following__username')
