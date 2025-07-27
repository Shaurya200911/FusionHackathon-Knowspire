# userauth/test_streaks.py
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from django.utils import timezone

from userauth.models import UserProfile
from userauth.services.streaks import apply_daily_streak, BASE_DAILY_XP, BONUS_EVERY, BONUS_XP

User = get_user_model()


class StreakTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.user = User.objects.create_user(username="test", password="pass")

    def _get_profile(self):
        return UserProfile.objects.get(user=self.user)

    def test_daily_increment_and_bonus(self):
        """
        Day 1..5 => streak goes 1..5, +5 XP each day, +5 extra on day 5.
        """
        start = timezone.now().replace(hour=9, minute=0, second=0, microsecond=0)

        total_xp = 0

        # Day 1
        _, xp, updated = apply_daily_streak(self.user, now=start)
        p = self._get_profile()
        self.assertTrue(updated)
        self.assertEqual(p.current_streak, 1)
        self.assertEqual(xp, BASE_DAILY_XP)
        total_xp += xp

        # Days 2..5
        for i in range(1, 5):
            fake_now = start + timedelta(days=i)
            _, xp, updated = apply_daily_streak(self.user, now=fake_now)
            p = self._get_profile()

            self.assertTrue(updated)
            self.assertEqual(p.current_streak, i + 1)

            # every BONUS_EVERY-th day: extra
            if (i + 1) % BONUS_EVERY == 0:
                self.assertEqual(xp, BASE_DAILY_XP + BONUS_XP)
            else:
                self.assertEqual(xp, BASE_DAILY_XP)

            total_xp += xp

        p.refresh_from_db()
        self.assertEqual(p.current_streak, 5)
        self.assertEqual(p.longest_streak, 5)
        self.assertEqual(p.xp_total, total_xp)

    def test_gap_resets_streak(self):
        base = timezone.now().replace(hour=9, minute=0, second=0, microsecond=0)

        # Day 1 -> 1
        apply_daily_streak(self.user, now=base)

        # Day 2 -> 2
        apply_daily_streak(self.user, now=base + timedelta(days=1))

        # Gap >= 2 days (jump to day 5)
        apply_daily_streak(self.user, now=base + timedelta(days=4))

        p = self._get_profile()
        self.assertEqual(p.current_streak, 1)
        self.assertEqual(p.longest_streak, 2)

    def test_same_day_does_not_increment_twice(self):
        now = timezone.now().replace(hour=9, minute=0, second=0, microsecond=0)
        _, xp1, updated1 = apply_daily_streak(self.user, now=now)
        p = self._get_profile()

        self.assertTrue(updated1)
        streak_1 = p.current_streak
        xp_total_1 = p.xp_total

        # Same calendar day
        _, xp2, updated2 = apply_daily_streak(self.user, now=now + timedelta(hours=3))
        p.refresh_from_db()

        self.assertFalse(updated2)
        self.assertEqual(xp2, 0)
        self.assertEqual(p.current_streak, streak_1)
        self.assertEqual(p.xp_total, xp_total_1)
