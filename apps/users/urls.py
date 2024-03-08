from django.urls import path

from .views import get_users, get_user, change_password, user_register, login


urlpatterns = [
    path("", get_users, name="get_users"),
    path("<uuid:id>/", get_user, name="get_user"),
    path("change_password/", change_password, name="change_password"),
    path("user_register/", user_register, name="user_register"),
    path("login/", login, name="login"),
]
