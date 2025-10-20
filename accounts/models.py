from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone



#  ACCOUNT CHOICES

ACCOUNT_TYPES = [
    ('normal', 'Normal Account'),
    ('business', 'Business Account'),
    ('premium', 'Premium Account'),
]

BUSINESS_TYPES = [
    ('store', 'Store'),
    ('service', 'Service'),
    ('ngo', 'Non-Governmental Organization'),
    ('govt', 'Government Organization'),
]



#  UPLOAD PATH

def profile_upload_path(instance, filename):
    return f"profiles/{instance.username}/{filename}"



#  CUSTOM USER MODEL

class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    profile_image = models.ImageField(upload_to=profile_upload_path, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    # Account type
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default='normal')

    # Business info (optional)
    business_name = models.CharField(max_length=100, blank=True, null=True)
    business_category = models.CharField(max_length=100, blank=True, null=True)
    business_subcategory = models.CharField(max_length=100, blank=True, null=True)
    business_type = models.CharField(max_length=50, choices=BUSINESS_TYPES, blank=True, null=True)

    # Location & contact
    country = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=150, blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)

    # Status fields
    followers_count = models.PositiveIntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    verification_badge = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    def is_following(self, user):
        """Check if this user is following another user."""
        return Follow.objects.filter(follower=self, following=user).exists()



#  FOLLOW MODEL

class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following_set', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='followers_set', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        verbose_name = "Follow"
        verbose_name_plural = "Follows"

    def __str__(self):
        return f"{self.follower.username} → {self.following.username}"



#  EMAIL VERIFICATION

class EmailVerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.code}"



#  USER RATING

class UserRating(models.Model):
    rated_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings_received')
    rated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings_given')
    rating = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('rated_user', 'rated_by')

    def __str__(self):
        return f"{self.rated_by.username} rated {self.rated_user.username} ({self.rating})"