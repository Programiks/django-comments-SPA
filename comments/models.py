from django.core.validators import RegexValidator
from django.db import models

from .validators import validate_attachment, validate_comment_html


username_validator = RegexValidator(
    regex=r"^[A-Za-z0-9]+$",
    message="User Name may contain only Latin letters and digits.",
)


class Comment(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PUBLISHED = "published"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PUBLISHED, "Published"),
    ]

    author_name = models.CharField(
        max_length=100,
        validators=[username_validator],
    )
    email = models.EmailField()
    home_page = models.URLField(blank=True)
    text = models.TextField(
        validators=[validate_comment_html],
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="replies",
        null=True,
        blank=True,
    )

    attachment = models.FileField(
        upload_to="attachments/%Y/%m/%d/",
        validators=[validate_attachment],
        null=True,
        blank=True,
    )

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["author_name"]),
            models.Index(fields=["email"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.author_name}: {self.text[:50]}"
