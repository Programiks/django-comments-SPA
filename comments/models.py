"""Django models for the comment system."""

from django.core.exceptions import ValidationError
from django.core.validators import (MaxLengthValidator, MinLengthValidator,
                                    RegexValidator)
from django.db import models

from .validators import validate_attachment, validate_comment_html

# Validator for author_name: only Latin letters, digits,
# and underscores allowed
username_validator = RegexValidator(
    regex=r"^[A-Za-z0-9_]+$",
    message="User Name may contain only Latin letters, digits, "
            "and underscore.",
)


class Comment(models.Model):
    """
    Model representing a user comment.

    Supports nested replies via self-referential ForeignKey.
    Comments can be pending or published based on status field.
    """

    STATUS_PENDING = "pending"
    STATUS_PUBLISHED = "published"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PUBLISHED, "Published"),
    ]

    author_name = models.CharField(
        max_length=100,
        validators=[username_validator],
        help_text="Author's display name "
                  "(Latin letters, digits, underscores only).",
    )
    email = models.EmailField(
        help_text="Author's email address (required).",
    )
    home_page = models.URLField(
        blank=True,
        help_text="Optional author website URL.",
    )
    text = models.TextField(
        validators=[
            validate_comment_html,  # Custom HTML sanitization
            MinLengthValidator(2),  # Minimum 2 characters
            MaxLengthValidator(2000),  # Maximum 2000 characters
        ],
        help_text="Comment text (2–2000 characters, HTML sanitized).",
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="replies",
        null=True,
        blank=True,
        help_text="Parent comment for nested replies "
                  "(None for top-level comments).",
    )

    attachment = models.FileField(
        upload_to="attachments/%Y/%m/%d/",
        validators=[validate_attachment],
        null=True,
        blank=True,
        help_text="Optional file attachment (images, documents).",
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="Author's IP address (for moderation/spam detection).",
    )
    user_agent = models.TextField(
        blank=True,
        help_text="Author's browser user agent string.",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the comment was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the comment was last updated.",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        help_text="Comment status: pending or published.",
    )

    class Meta:
        """Meta options for Comment model."""

        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["author_name"]),
            models.Index(fields=["email"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        """Return string representation of the comment."""
        return f"{self.author_name}: {self.text[:50]}"

    def clean(self):
        """
        Validate comment text for security.

        Raises:
            ValidationError: If text contains <script> tags (XSS prevention).
        """
        if '<script' in self.text.lower():
            raise ValidationError({'text': 'Script tags are not allowed.'})
