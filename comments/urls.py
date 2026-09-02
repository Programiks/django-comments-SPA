"""
URL configuration for the comment system.

This module defines URL patterns for comment-related views:
- Comment list and submission
- CAPTCHA image generation
- Comment preview (AJAX)
"""

from django.urls import path

from . import views

# Application namespace for URL reversing
app_name = "comments"

# URL patterns for comment system endpoints
urlpatterns = [
    # Main comment list view (GET) and comment submission (POST)
    path("", views.comment_list, name="comment_list"),

    # CAPTCHA image endpoint for spam prevention
    path("captcha/", views.captcha_image, name="captcha_image"),

    # AJAX endpoint for live comment preview before submission
    path("preview/", views.comment_preview, name="comment_preview"),
]
