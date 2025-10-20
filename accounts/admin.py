from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, EmailVerificationCode, UserRating, Follow


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Disbod Account Details', {
            'fields': (
                'profile_image',
                'bio',
                'account_type',
                'business_name',
                'business_category',
                'business_subcategory',
                'location',
                'contact_number',
                'country',
                'region',
                'city',
                'followers_count',
                'is_email_verified',
                'verification_badge',
                'is_suspended',
                'is_verified',
            ),
        }),
    )

    list_display = (
        'username',
        'email',
        'account_type',
        'business_name',
        'is_email_verified',
        'verification_badge',
        'is_verified',
        'is_suspended',
    )

    search_fields = ('username', 'email', 'business_name', 'country', 'city')
    list_filter = ('account_type', 'is_email_verified', 'is_verified', 'is_suspended')
    ordering = ('username',)


@admin.register(EmailVerificationCode)
class EmailVerificationCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at', 'is_verified')
    search_fields = ('user__username', 'code')
    list_filter = ('is_verified', 'created_at')


@admin.register(UserRating)
class UserRatingAdmin(admin.ModelAdmin):
    list_display = ('rated_user', 'rated_by', 'rating', 'created_at')
    search_fields = ('rated_user__username', 'rated_by__username')
    list_filter = ('rating', 'created_at')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    search_fields = ('follower__username', 'following__username')
    list_filter = ('created_at',)