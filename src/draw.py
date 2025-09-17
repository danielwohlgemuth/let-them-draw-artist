import random
from PIL import Image, ImageColor, ImageDraw


def _draw_square(draw, size, color):
    draw.rectangle(
        [0, 0, size, size],
        fill=color
    )

def _draw_circle(draw, size, color):
    draw.ellipse(
        [0, 0, size, size],
        fill=color
    )

def _draw_hypnotic_squares(draw, size, color):
    final_size = 3
    offset = 2
    tile_step = (size - offset * 2) / 4
    start_size = tile_step
    directions = [-1, 0, 1]

    def draw_square(x, y, width, height, x_movement, y_movement, steps, start_steps):
        draw.rectangle([x, y, x + width, y + height], outline=color, width=2)

        if steps >= 0:
            new_size = (start_size * (steps / start_steps)) + final_size
            new_x = x + (width - new_size) / 2
            new_y = y + (height - new_size) / 2
            new_x = new_x - ((x - new_x) / (steps + 2)) * x_movement
            new_y = new_y - ((y - new_y) / (steps + 2)) * y_movement
            draw_square(new_x, new_y, new_size, new_size, x_movement, y_movement, steps - 1, start_steps)

    for x in range(offset, size - offset, int(tile_step)):
        for y in range(offset, size - offset, int(tile_step)):
            start_steps = 2 + int(random.random() * 4)
            x_dir = random.choice(directions)
            y_dir = random.choice(directions)
            draw_square(x, y, start_size, start_size, x_dir, y_dir, start_steps - 1, start_steps - 1)

def draw_image(shape, color, size=512, scale_factor=4):
    """
    Draw an image with the specified shape and color, with anti-aliasing.

    Args:
        shape (str): The shape to draw ('square' or 'circle').
        color (str): The color to use (any valid ImageColor string).
        size (int): The width and height of the output image in pixels.
        scale_factor (int): Multiplier for anti-aliasing (higher = smoother but slower).

    Returns:
        PIL.Image: The generated image with anti-aliased edges.
    """
    large_size = size * scale_factor
    img = Image.new('RGBA', (large_size, large_size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    try:
        # https://drafts.csswg.org/css-color-4/#named-colors
        rgb_color = ImageColor.getrgb(color)
        rgba_color = rgb_color + (255,)
    except ValueError:
        rgba_color = (0, 0, 0, 255)

    margin = large_size // 8
    shape_size = large_size - 2 * margin

    shape_img = Image.new('RGBA', (shape_size, shape_size), (0, 0, 0, 0))
    shape_draw = ImageDraw.Draw(shape_img)

    shape_methods = {
        'square': _draw_square,
        'circle': _draw_circle,
        'hypnotic squares': _draw_hypnotic_squares
    }

    draw_method = shape_methods.get(shape.lower())
    if draw_method:
        draw_method(shape_draw, shape_size, rgba_color)

    img.paste(shape_img, (margin, margin), shape_img)

    img = img.resize((size, size), Image.Resampling.LANCZOS)

    if img.mode == 'RGBA':
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])  # 3 is the alpha channel
        img = background

    return img
