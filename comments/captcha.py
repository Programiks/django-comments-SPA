import random
import string
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont


CAPTCHA_ALPHABET = string.ascii_uppercase + string.digits
CAPTCHA_LENGTH = 6
CAPTCHA_WIDTH = 180
CAPTCHA_HEIGHT = 60


def generate_captcha_code():
    """Return a random CAPTCHA code."""
    return "".join(random.choices(CAPTCHA_ALPHABET, k=CAPTCHA_LENGTH))


def generate_captcha_image(code):
    """Return a PNG CAPTCHA image as bytes."""
    image = Image.new("RGB", (CAPTCHA_WIDTH, CAPTCHA_HEIGHT), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("arial.ttf", 24)

    for _ in range(12):
        x1 = random.randint(0, CAPTCHA_WIDTH)
        y1 = random.randint(0, CAPTCHA_HEIGHT)
        x2 = random.randint(0, CAPTCHA_WIDTH)
        y2 = random.randint(0, CAPTCHA_HEIGHT)
        draw.line((x1, y1, x2, y2), fill="lightgray", width=1)

    text_box = draw.textbbox((0, 0), code, font=font)
    text_width = text_box[2] - text_box[0]
    text_height = text_box[3] - text_box[1]

    x = (CAPTCHA_WIDTH - text_width) // 2
    y = (CAPTCHA_HEIGHT - text_height) // 2

    draw.text((x, y), code, fill="black", font=font)

    image_bytes = BytesIO()
    image.save(image_bytes, format="PNG")
    return image_bytes.getvalue()
