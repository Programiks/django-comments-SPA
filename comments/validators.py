import bleach
from django.core.exceptions import ValidationError


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
