import bleach
from django.core.exceptions import ValidationError
from pathlib import Path

from PIL import Image, UnidentifiedImageError


ALLOWED_TAGS = ["a", "code", "i", "strong"]
ALLOWED_ATTRIBUTES = {
    "a": ["href", "title"],
}
ALLOWED_PROTOCOLS = ["http", "https", "mailto"]


def sanitize_comment_html(value: str) -> str:
    return bleach.clean(
        value,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )


def validate_comment_html(value: str) -> None:
    sanitized_value = sanitize_comment_html(value)

    if sanitized_value != value:
        raise ValidationError(
            "Comment text contains unsupported or unsafe HTML."
        )


ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".gif", ".png"}
ALLOWED_ATTACHMENT_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | {".txt"}
MAX_TEXT_FILE_SIZE = 100 * 1024


def validate_attachment(file) -> None:
    extension = Path(file.name).suffix.lower()

    if extension not in ALLOWED_ATTACHMENT_EXTENSIONS:
        raise ValidationError(
            "Attachment must be a JPG, GIF, PNG, or TXT file."
        )

    if extension == ".txt":
        if file.size > MAX_TEXT_FILE_SIZE:
            raise ValidationError(
                "TXT attachment must not exceed 100 KB."
            )
        return

    try:
        image = Image.open(file)
        image.verify()
    except (UnidentifiedImageError, OSError):
        raise ValidationError(
            "Attachment must be a valid image file."
        )

    finally:
        file.seek(0)
