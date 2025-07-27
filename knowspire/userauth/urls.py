from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("", views.index_view, name="home"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("paywall/", views.paywall_view, name="paywall"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("leaderboard/", views.leaderboard_view, name="leaderboard"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
]