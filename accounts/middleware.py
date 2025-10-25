# accounts/middleware.py

from django.http import JsonResponse
from django.utils import timezone

class UserSuspensionMiddleware:
    """Prevents suspended or blocked users from performing any action."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            # Check suspension expiry
            if user.is_suspended and user.suspended_until:
                if timezone.now() > user.suspended_until:
                    user.unsuspend()
                else:
                    return JsonResponse({
                        "error": "Your account is suspended until " + str(user.suspended_until)
                    }, status=403)

            # Check permanent block
            if not user.is_active:
                return JsonResponse({
                    "error": "Your account has been blocked by Disbod Admin."
                }, status=403)

            # Auto-downgrade expired premium
            user.downgrade_if_expired()

        return self.get_response(request)
