from django.urls import path

from .views import change_password, delete_user, get_current_user, get_user, get_users, login, logout, user_register

urlpatterns = [
    path("", get_users, name="get_users"),
    path("me/", get_current_user, name="get_current_user"),
    path("<uuid:id>/", get_user, name="get_user"),
    path("change_password/", change_password, name="change_password"),
    path("user_register/", user_register, name="user_register"),
    path("login/", login, name="login"),
    path("logout/", logout, name="logout"),
    path("delete/<uuid:id>/", delete_user, name="delete_user"),
]
