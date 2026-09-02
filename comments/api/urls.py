"""
URL configuration for the comments API.
"""

from django.urls import path

from .views import CommentCreateView, LoginView, RegisterView

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="api-register"),
    path("auth/login/", LoginView.as_view(), name="api-login"),
    path("comments/", CommentCreateView.as_view(), name="api-comment-create"),
]
