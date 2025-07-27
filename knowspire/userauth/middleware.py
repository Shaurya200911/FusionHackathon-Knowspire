from django.utils import timezone
from .services.streaks import apply_daily_streak

class StreakMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Safe to call every request: it will only increment once/day
            apply_daily_streak(request.user, now=timezone.now())
        return self.get_response(request)
