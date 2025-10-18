# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

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


def profile_upload_path(instance, filename):
    return f"profiles/{instance.username}/{filename}"


class User(AbstractUser):
    # Note: AbstractUser already provides username, first_name, last_name, email, password, is_active etc.
    email = models.EmailField(unique=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default='normal')
    is_email_verified = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to=profile_upload_path, blank=True, null=True)
    phone_number = models.CharField(max_length=30, blank=True, null=True)

    # Location
    country = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)

    # Business fields (only for business/premium)
    business_name = models.CharField(max_length=50, blank=True, null=True, unique=True)
    business_type = models.CharField(max_length=50, choices=BUSINESS_TYPES, blank=True, null=True)
    sub_category = models.CharField(max_length=100, blank=True, null=True)
    verification_badge = models.BooleanField(default=False)

    # Follow relationship: many-to-many self
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)

    is_suspended = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    REQUIRED_FIELDS = ['email']  # when creating via createsuperuser

    def __str__(self):
        return self.username



class EmailVerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.code}"


class UserRating(models.Model):
    rated_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings_received')
    rated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings_given')
    rating = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rated_by} rated {self.rated_user}"


class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following_user', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='followers_user', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.follower} follows {self.following}"