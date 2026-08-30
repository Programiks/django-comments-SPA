from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from PIL import Image


MAX_IMAGE_WIDTH = 320
MAX_IMAGE_HEIGHT = 240
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".gif", ".png"}


def resize_attachment_image(attachment) -> None:
    """Resize an image in place if it exceeds 320x240 pixels."""
    extension = Path(attachment.name).suffix.lower()

    if extension not in IMAGE_EXTENSIONS:
        return

    image = Image.open(attachment)
    image.thumbnail((MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT))

    output = BytesIO()

    image_format = image.format
    if image_format == "JPEG" and image.mode in {"RGBA", "P"}:
        image = image.convert("RGB")

    image.save(output, format=image_format)
    output.seek(0)

    attachment.save(
        attachment.name,
        ContentFile(output.read()),
        save=False,
    )
