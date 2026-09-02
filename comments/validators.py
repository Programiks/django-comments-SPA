"""
Custom validators for comment system.

This module provides validation functions for:
- Comment HTML sanitization (XSS prevention)
- Attachment file type and size validation
"""

from pathlib import Path

import bleach
from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError

# Allowed HTML tags in comment text (whitelist for security)
ALLOWED_TAGS = ["a", "code", "i", "strong"]

# Allowed HTML attributes per tag (only safe attributes permitted)
ALLOWED_ATTRIBUTES = {
    "a": ["href", "title"],
}

# Allowed URL protocols in links
# (prevent javascript: and other dangerous protocols)
ALLOWED_PROTOCOLS = ["http", "https", "mailto"]


def sanitize_comment_html(value: str) -> str:
    """
    Sanitize comment HTML by allowing only safe tags, attributes,
    and protocols.

    This function uses bleach to strip all HTML tags except those
    in ALLOWED_TAGS, and removes any unsafe attributes or protocols.

    Args:
        value: Raw HTML string from user input.

    Returns:
        str: Sanitized HTML string with only allowed tags and attributes.
    """
    return bleach.clean(
        value,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )


def validate_comment_html(value: str) -> None:
    """
    Validate that comment HTML uses only allowed tags and attributes.

    This validator ensures that user-submitted HTML does not contain
    any disallowed tags or attributes. If the sanitized HTML differs
    from the input, a ValidationError is raised.

    Args:
        value: Raw HTML string from user input.

    Raises:
        ValidationError: If the HTML contains unsupported or unsafe elements.

    Notes:
        - Normalizes line endings to avoid false positives due to \r\n vs \n
        - Uses strip=True to remove disallowed tags entirely
    """
    # Normalize line endings to match bleach behavior
    normalized = value.replace("\r\n", "\n").replace("\r", "\n")

    sanitized_value = sanitize_comment_html(normalized)

    if sanitized_value != normalized:
        raise ValidationError(
            "Comment text contains unsupported or unsafe HTML."
        )


# Allowed file extensions for image attachments
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".gif", ".png"}

# Allowed file extensions for all attachments (images + text files)
ALLOWED_ATTACHMENT_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | {".txt"}

# Maximum file size for text attachments (100 KB)
MAX_TEXT_FILE_SIZE = 100 * 1024


def validate_attachment(file) -> None:
    """
    Validate attachment file type and size.

    This validator ensures that uploaded attachments are either:
    - Valid image files (JPG, PNG, GIF)
    - Text files (TXT) not exceeding 100 KB

    Args:
        file: Django FileField instance to validate.

    Raises:
        ValidationError: If the file type is invalid or size exceeds limits.

    Notes:
        - Image files are verified using PIL to ensure they are not corrupted
        - File pointer is reset after validation to allow subsequent reads
    """
    extension = Path(file.name).suffix.lower()

    # Check if file extension is allowed
    if extension not in ALLOWED_ATTACHMENT_EXTENSIONS:
        raise ValidationError(
            "Attachment must be a JPG, GIF, PNG, or TXT file."
        )

    # Validate text file size
    if extension == ".txt":
        if file.size > MAX_TEXT_FILE_SIZE:
            raise ValidationError(
                "TXT attachment must not exceed 100 KB."
            )
        return

    # Validate image file integrity
    try:
        image = Image.open(file)
        image.verify()
    except (UnidentifiedImageError, OSError):
        raise ValidationError(
            "Attachment must be a valid image file."
        )
    finally:
        # Reset file pointer for subsequent operations
        file.seek(0)
