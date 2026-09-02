"""
CAPTCHA generation utilities for comment system.

This module provides functions for:
- Generating random CAPTCHA codes
- Creating CAPTCHA images with noise lines for bot protection
"""

import random
import string
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

# Allowed characters in CAPTCHA codes (uppercase letters and digits only)
CAPTCHA_ALPHABET = string.ascii_uppercase + string.digits

# Length of generated CAPTCHA codes
CAPTCHA_LENGTH = 6

# Dimensions of CAPTCHA image in pixels
CAPTCHA_WIDTH = 180
CAPTCHA_HEIGHT = 60


def generate_captcha_code():
    """
    Generate a random CAPTCHA code.

    This function creates a random string of uppercase letters and digits
    with a fixed length defined by CAPTCHA_LENGTH.

    Returns:
        str: Random CAPTCHA code (e.g., "A7K9M2").

    Notes:
        - Uses random.choices for uniform distribution
        - Code consists only of uppercase letters and digits
    """
    return "".join(random.choices(CAPTCHA_ALPHABET, k=CAPTCHA_LENGTH))


def generate_captcha_image(code):
    """
    Generate a CAPTCHA image as PNG bytes.

    This function creates a CAPTCHA image with the given code, adding
    random noise lines to make automated recognition more difficult.

    Args:
        code: String containing the CAPTCHA code to display.

    Returns:
        bytes: PNG-encoded image data.

    Notes:
        - Image has white background with black text
        - 12 random gray noise lines are added for obfuscation
        - Text is centered horizontally and vertically
        - Requires 'arial.ttf' font to be available on the system
    """
    # Create white background image
    image = Image.new("RGB", (CAPTCHA_WIDTH, CAPTCHA_HEIGHT), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=24)

    # Add random noise lines for bot protection
    for _ in range(12):
        x1 = random.randint(0, CAPTCHA_WIDTH)
        y1 = random.randint(0, CAPTCHA_HEIGHT)
        x2 = random.randint(0, CAPTCHA_WIDTH)
        y2 = random.randint(0, CAPTCHA_HEIGHT)
        draw.line((x1, y1, x2, y2), fill="lightgray", width=1)

    # Calculate text bounding box for centering
    text_box = draw.textbbox((0, 0), code, font=font)
    text_width = text_box[2] - text_box[0]
    text_height = text_box[3] - text_box[1]

    # Center text in the image
    x = (CAPTCHA_WIDTH - text_width) // 2
    y = (CAPTCHA_HEIGHT - text_height) // 2

    draw.text((x, y), code, fill="black", font=font)

    # Convert image to PNG bytes
    image_bytes = BytesIO()
    image.save(image_bytes, format="PNG")
    return image_bytes.getvalue()
