from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone
from datetime import timedelta
from .models import User, EmailVerificationCode, UserRating, Follow



#  USER ADMIN CONFIGURATION

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin interface for User model with Disbod actions."""

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
                'upgraded_until',
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
        'is_active',
        'upgraded_until',
    )

    search_fields = ('username', 'email', 'business_name', 'country', 'city')
    list_filter = ('account_type', 'is_email_verified', 'is_verified', 'is_suspended', 'is_active')
    ordering = ('username',)

    # ========== Admin Actions ==========
    @admin.action(description="Suspend selected users for 7 days")
    def suspend_users(self, request, queryset):
        for user in queryset:
            user.suspend(days=7)
        self.message_user(request, "Selected users suspended for 7 days.")

    @admin.action(description="Unsuspend selected users")
    def unsuspend_users(self, request, queryset):
        for user in queryset:
            user.unsuspend()
        self.message_user(request, "Selected users unsuspended successfully.")

    @admin.action(description="Upgrade selected users to Premium (30 days)")
    def upgrade_to_premium(self, request, queryset):
        for user in queryset:
            user.upgrade(plan_type='premium', days=30)
        self.message_user(request, "Selected users upgraded to Premium for 30 days.")

    @admin.action(description="Send caution message to selected users")
    def send_caution(self, request, queryset):
        message = "Please adhere to Disbod's community guidelines."
        for user in queryset:
            user.caution(message)
        self.message_user(request, "Caution messages sent to selected users.")

    @admin.action(description="Block selected users (deactivate)")
    def block_users(self, request, queryset):
        for user in queryset:
            user.block()
        self.message_user(request, "Selected users blocked successfully.")

    actions = [
        'suspend_users',
        'unsuspend_users',
        'upgrade_to_premium',
        'send_caution',
        'block_users',
    ]



#  FOLLOW ADMIN

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    search_fields = ('follower__username', 'following__username')
    list_filter = ('created_at',)



#  EMAIL VERIFICATION ADMIN

@admin.register(EmailVerificationCode)
class EmailVerificationCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at', 'is_verified')
    search_fields = ('user__username', 'code')
    list_filter = ('is_verified', 'created_at')



#  USER RATING ADMIN

@admin.register(UserRating)
class UserRatingAdmin(admin.ModelAdmin):
    list_display = ('rated_user', 'rated_by', 'rating', 'created_at')
    search_fields = ('rated_user__username', 'rated_by__username')
    list_filter = ('rating', 'created_at')
