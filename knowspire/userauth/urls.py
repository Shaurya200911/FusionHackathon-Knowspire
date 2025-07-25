from django.urls import path
from . import views

urlpatterns = [
    path("", views.index_view, name="home"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("paywall/", views.paywall_view, name="paywall"),
]