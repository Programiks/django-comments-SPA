from django.urls import path
from . import views

app_name = "comments"

urlpatterns = [
    path("", views.comment_list, name="comment_list"),
    path("captcha/", views.captcha_image, name="captcha_image"),
]
