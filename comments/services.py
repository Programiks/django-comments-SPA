"""
Image processing utilities for comment attachments.

This module provides functions to resize and optimize images
before saving them as comment attachments.
"""

from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from PIL import Image

# Maximum dimensions for resized images
MAX_IMAGE_WIDTH = 320
MAX_IMAGE_HEIGHT = 240

# Supported image file extensions
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".gif", ".png"}


def resize_attachment_image(attachment) -> None:
    """
    Resize an image attachment in place if it exceeds maximum dimensions.

    This function resizes images to fit within 320x240 pixels while maintaining
    aspect ratio. Non-image files and unsupported formats are skipped.

    Args:
        attachment: A Django FileField or ImageField instance.

    Returns:
        None: The attachment is modified in place.

    Notes:
        - Converts RGBA/PNG images to RGB for JPEG compatibility.
        - Preserves the original image format when saving.
    """
    extension = Path(attachment.name).suffix.lower()

    # Skip non-image files
    if extension not in IMAGE_EXTENSIONS:
        return

    # Open and resize the image
    image = Image.open(attachment)
    image.thumbnail((MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT))

    # Prepare output buffer
    output = BytesIO()

    # Handle transparency for JPEG format
    image_format = image.format
    if image_format == "JPEG" and image.mode in {"RGBA", "P"}:
        image = image.convert("RGB")

    # Save resized image to buffer
    image.save(output, format=image_format)
    output.seek(0)

    # Replace original attachment with resized version
    attachment.save(
        attachment.name,
        ContentFile(output.read()),
        save=False,
    )
