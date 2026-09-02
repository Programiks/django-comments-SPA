"""
Django application configuration for the comments app.

This module defines the CommentsConfig class, which configures the
comments Django application and its settings.
"""

from django.apps import AppConfig


class CommentsConfig(AppConfig):
    """
    Configuration class for the comments Django application.

    This class extends AppConfig to provide custom configuration
    for the comments app, including model field defaults.

    Attributes:
        default_auto_field: Default auto-incrementing primary key field type.
        name: Python path to the comments app package.

    Notes:
        - BigAutoField is used for 64-bit integer primary keys
        - This configuration is automatically loaded by Django
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "comments"
