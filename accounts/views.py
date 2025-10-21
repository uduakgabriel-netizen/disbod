from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import EmailVerificationCode
import random
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .serializers import ProfileSerializer
from .models import Follow
from .serializers import FollowSerializer, ExploreSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, filters
from django.db.models import Q
from rest_framework import status, permissions

User = get_user_model()


class RegisterView(APIView):
    def post(self, request):
        email = request.data.get("email")

        # Check if email provided
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user already exists
        user, created = User.objects.get_or_create(email=email)

        # Generate a random 6-digit code
        code = random.randint(100000, 999999)

        # Save verification code
        EmailVerificationCode.objects.create(user=user, code=str(code))

        # (Optional) Send the code to user email (we’ll implement actual sending later)
        print(f"Verification code for {email}: {code}")  # Debug only

        return Response({
            "message": "Verification code sent to your email",
            "email": email
        }, status=status.HTTP_201_CREATED)


class VerifyEmailView(APIView):
    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")

        if not email or not code:
            return Response(
                {"error": "Email and verification code are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            verification = EmailVerificationCode.objects.filter(
                user=user, code=code, is_used=False
            ).latest("created_at")
        except EmailVerificationCode.DoesNotExist:
            return Response(
                {"error": "Invalid or expired verification code"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Optional: Add expiration (e.g. 10 minutes)
        expiration_time = verification.created_at + timedelta(minutes=10)
        if timezone.now() > expiration_time:
            return Response(
                {"error": "Verification code expired"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mark code as used
        verification.is_used = True
        verification.save()

        # Mark user as verified and active
        user.is_verified = True
        user.is_active = True
        user.save()

        return Response(
            {"message": "Email verified successfully. You can now log in."},
            status=status.HTTP_200_OK
        )
        
        
class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid email or password"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.check_password(password):
            return Response(
                {"error": "Invalid email or password"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_verified:
            return Response(
                {"error": "Please verify your email before logging in."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Login successful",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            }
        }, status=status.HTTP_200_OK)
        
        
# accounts/views.py


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Invalid token or token already blacklisted"}, status=status.HTTP_400_BAD_REQUEST)



class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FollowUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        target_user = User.objects.filter(id=user_id).first()
        if not target_user:
            return Response({"error": "User not found"}, status=404)

        if request.user == target_user:
            return Response({"error": "You cannot follow yourself"}, status=400)

        if Follow.objects.filter(follower=request.user, following=target_user).exists():
            return Response({"message": "Already following this user"}, status=400)

        Follow.objects.create(follower=request.user, following=target_user)
        target_user.followers_count = Follow.objects.filter(following=target_user).count()
        target_user.save()
        return Response({"message": f"You are now following {target_user.username}"}, status=201)


class UnfollowUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id):
        target_user = User.objects.filter(id=user_id).first()
        if not target_user:
            return Response({"error": "User not found"}, status=404)

        follow = Follow.objects.filter(follower=request.user, following=target_user)
        if not follow.exists():
            return Response({"error": "You are not following this user"}, status=400)

        follow.delete()
        target_user.followers_count = Follow.objects.filter(following=target_user).count()
        target_user.save()
        return Response({"message": f"You have unfollowed {target_user.username}"}, status=200)
    
    
class ExploreView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("q", "")
        country = request.query_params.get("country", "")
        region = request.query_params.get("region", "")
        city = request.query_params.get("city", "")
        category = request.query_params.get("category", "")

        users = User.objects.filter(
            Q(account_type__in=["business", "premium"]) &
            Q(followers_count__gte=20)
        )

        if query:
            users = users.filter(
                Q(username__icontains=query) |
                Q(business_name__icontains=query)
            )
        if country:
            users = users.filter(country__icontains=country)
        if region:
            users = users.filter(region__icontains=region)
        if city:
            users = users.filter(city__icontains=city)
        if category:
            users = users.filter(business_category__icontains=category)

        serializer = ExploreSerializer(users, many=True)
        return Response(serializer.data)
