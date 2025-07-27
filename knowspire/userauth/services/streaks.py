# userauth/services/streaks.py
from datetime import timedelta
from django.db import transaction
from django.utils import timezone

from userauth.models import UserProfile, Activity

BASE_DAILY_XP = 5
BONUS_EVERY = 5
BONUS_XP = 5
DEBUG_STREAK = False  # flip to True to see prints while running tests


def _to_local_date(dt):
    # Always convert to local time first, then take the date
    return timezone.localtime(dt).date()


@transaction.atomic
def apply_daily_streak(user, *, now=None):
    """
    Award daily streak XP:
    - +5 XP every day the user shows up (once per *calendar* day)
    - +5 extra XP on every 5th day (5, 10, 15, ...)
    - Reset the streak if the user misses 1+ days.
    Returns: (profile, xp_awarded, updated_flag)
    """
    if now is None:
        now = timezone.now()

    today = _to_local_date(now)

    # Lock the row so parallel requests don't double count
    profile, _ = UserProfile.objects.select_for_update().get_or_create(user=user)

    last_seen_date = None
    if profile.last_activity_at:
        last_seen_date = _to_local_date(profile.last_activity_at)

    if DEBUG_STREAK:
        print(f"[apply_daily_streak] user={user.username} today={today} "
              f"last_seen_date={last_seen_date} before_streak={profile.current_streak}")

    # Already counted for today
    if last_seen_date == today:
        if DEBUG_STREAK:
            print("[apply_daily_streak] already updated today -> no-op")
        return profile, 0, False

    # First time or continued streak?
    if last_seen_date is None:
        profile.current_streak = 1
    else:
        gap = (today - last_seen_date).days
        if DEBUG_STREAK:
            print(f"[apply_daily_streak] gap={gap}")
        if gap == 1:
            profile.current_streak += 1
        else:
            # missed days -> reset
            profile.current_streak = 1

    # Longest
    if profile.current_streak > profile.longest_streak:
        profile.longest_streak = profile.current_streak

    # XP
    xp_gain = BASE_DAILY_XP
    if profile.current_streak % BONUS_EVERY == 0:
        xp_gain += BONUS_XP

    profile.xp_total += xp_gain
    profile.last_activity_at = now
    profile.save(update_fields=[
        "current_streak", "longest_streak", "xp_total", "last_activity_at"
    ])

    Activity.objects.create(
        user=user,
        type=Activity.STREAK_UPDATED,
        xp_delta=xp_gain,
        payload={
            "streak": profile.current_streak,
            "bonus": (xp_gain > BASE_DAILY_XP),
        },
    )

    if DEBUG_STREAK:
        print(f"[apply_daily_streak] UPDATED -> streak={profile.current_streak}, "
              f"longest={profile.longest_streak}, xp+={xp_gain}, xp_total={profile.xp_total}")

    return profile, xp_gain, True
