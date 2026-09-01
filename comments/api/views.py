"""
API views for authentication and comment creation.
"""

from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import RegisterSerializer, LoginSerializer
from comments.models import Comment


User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    """

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class LoginView(TokenObtainPairView):
    """
    API endpoint for user login and JWT token issuance.
    Returns access token + username + email.
    """

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        # response.data contains {"access": "...", "refresh": "..."}

        username = request.data.get("username")
        user = User.objects.filter(username=username).first()

        if user:
            response.data["username"] = user.username
            response.data["email"] = user.email or ""

        return response


class CommentCreateView(generics.CreateAPIView):
    """
    Protected API endpoint for creating comments.

    Requires a valid JWT token in the Authorization header.
    """

    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Create a new comment from the request data.

        Expected fields:
        - author_name (required)
        - email (optional)
        - text (required)
        """
        author_name = request.data.get("author_name")
        email = request.data.get("email")
        text = request.data.get("text")

        if not author_name or not text:
            return Response(
                {"detail": "author_name and text are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        comment = Comment.objects.create(
            author_name=author_name,
            email=email or "",
            text=text,
        )

        return Response(
            {"id": comment.id, "author_name": comment.author_name},
            status=status.HTTP_201_CREATED,
        )
