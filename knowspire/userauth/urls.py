from django.contrib.auth import logout
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index_view, name="home"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("paywall/", views.paywall_view, name="paywall"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("leaderboard/", views.leaderboard_view, name="leaderboard"),
    path("skills/", views.skills_view, name="skills"),
    path("skills/start/", views.start_skill_view, name="start_skill"),
    path("skills/<slug:slug>/", views.skill_detail_view, name="skill_detail"),
    path("skills/archive/<int:user_skill_id>/", views.archive_skill, name="archive_skill"),
    path("skills/download/<int:user_skill_id>/", views.download_skill_data, name="download_skill_data"),
    path("skills/delete/<int:user_skill_id>/", views.delete_skill, name="delete_skill"),
    path("logout/", views.logout_view, name="logout"),
]