from io import BytesIO
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent


def measure_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> Tuple[int, int]:
    l, t, r, b = draw.textbbox((0, 0), text, font=font, anchor="lt")
    return r - l, b - t


def get_dynamic_font_size(
        draw: ImageDraw.ImageDraw,
        text: str,
        font_path: str,
        max_font_size: int,
        min_font_size: int,
        available_width: int,
        side_padding: int,
) -> int:
    for size in range(max_font_size, min_font_size - 1, -1):
        font_candidate = ImageFont.truetype(font_path, size)
        text_width, _ = measure_text(draw, text, font_candidate)
        if text_width + 2 * side_padding <= available_width:
            return size
    return min_font_size


def draw_centered_text(
        draw: ImageDraw.ImageDraw,
        image: Image.Image,
        text: str,
        font_path: str,
        max_font_size: int,
        min_font_size: int,
        text_color: Tuple,
        margin: int,
        side_padding: int,
        min_side_margin: int,
        frame_fill: Tuple,
        frame_radius: int,
) -> None:
    available_width = image.width - 2 * min_side_margin

    font_size = get_dynamic_font_size(draw, text, font_path, max_font_size, min_font_size, available_width,
                                      side_padding)
    font = ImageFont.truetype(font_path, font_size)
    text_width, text_height = measure_text(draw, text, font)

    frame_top = margin
    frame_bottom = image.height - margin
    frame_height = frame_bottom - frame_top

    ideal_frame_left = (image.width - text_width) / 2 - side_padding
    ideal_frame_right = (image.width + text_width) / 2 + side_padding

    frame_left = max(ideal_frame_left, min_side_margin)
    frame_right = min(ideal_frame_right, image.width - min_side_margin)

    draw.rounded_rectangle(
        (frame_left, frame_top, frame_right, frame_bottom),
        radius=frame_radius,
        fill=frame_fill
    )

    text_x = frame_left + (frame_right - frame_left - text_width) / 2
    text_y = frame_top + (frame_height - text_height) / 2
    draw.text((text_x, text_y), text, font=font, fill=text_color, anchor="lt")


def draw_bottom_text(
        draw: ImageDraw.ImageDraw,
        image: Image.Image,
        bottom_text: str,
        font_path: str,
        max_font_size: int,
        min_font_size: int,
        text_color: Tuple,
        bottom_text_margin: int,
        bottom_side_padding: int,
        min_side_margin: int,
) -> None:
    available_width = image.width - 2 * min_side_margin - 2 * bottom_side_padding
    font_size = get_dynamic_font_size(draw, bottom_text, font_path, max_font_size, min_font_size, available_width, 0)
    font = ImageFont.truetype(font_path, font_size)
    text_width, text_height = measure_text(draw, bottom_text, font)

    text_x = (image.width - text_width) / 2
    text_y = image.height - text_height - bottom_text_margin
    draw.text((text_x, text_y), bottom_text, font=font, fill=text_color, anchor="lt")


def generate_image(
        domain: str,
        subdomain: Optional[str] = None,
        tld: Optional[str] = "ton",
        max_font_size: int = 100,
        min_font_size: int = 10,
        margin: int = 380,
        side_padding: int = 67,
        min_side_margin: int = 100,
        frame_radius: int = 77,
        bottom_text_margin: int = 100,
        bottom_max_font_size: int = 40,
        bottom_min_font_size: int = 20,
        bottom_side_padding: int = 20,
) -> bytes:
    if tld == "gram":
        font_path: str = f"{BASE_DIR}/fonts/Inter-SemiBold.ttf"
        frame_fill: Tuple[int, int, int, int] = (45, 45, 50, 255)
        text_color: Tuple[int, int, int] = (255, 255, 255)
        length = 1 if len(subdomain or domain) % 2 == 0 else 2
        bottom_text_color = text_color if length == 1 else (0, 0, 0)
    else:
        font_path: str = f"{BASE_DIR}/fonts/JetBrainsMono-ExtraBold.ttf"
        text_color: Tuple[int, int, int] = (0, 0, 0)
        frame_fill: Tuple[int, int, int] = (255, 255, 255)
        length = len(subdomain or domain) if len(subdomain or domain) < 11 else 11
        bottom_text_color = text_color

    if subdomain is not None and len(subdomain) > 28:
        subdomain = subdomain[:13] + "..." + subdomain[-12:]
    if len(domain) > 28:
        domain = domain[:13] + "..." + domain[-12:]

    header_text = f"{subdomain or domain}.{tld}"
    if len(header_text) > 28:
        header_text = header_text[:13] + "..." + header_text[-12:]

    image = Image.open(f"{BASE_DIR}/backgrounds/{tld}/{length}.png")
    draw = ImageDraw.Draw(image)

    draw_centered_text(
        draw,
        image,
        header_text,
        font_path,
        max_font_size,
        min_font_size,
        text_color,
        margin,
        side_padding,
        min_side_margin,
        frame_fill,
        frame_radius
    )

    if subdomain is not None:
        bottom_text = f"{subdomain}.{domain}.{tld}"
        draw_bottom_text(
            draw,
            image,
            bottom_text,
            font_path,
            bottom_max_font_size,
            bottom_min_font_size,
            bottom_text_color,
            bottom_text_margin,
            bottom_side_padding,
            min_side_margin
        )

    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()
