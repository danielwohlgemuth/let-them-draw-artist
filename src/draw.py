import random
import math
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

def _draw_tiled_lines(draw, size, color):
    step = max(20, size // 25)
    margin = step

    for x in range(margin, size - margin, step):
        for y in range(margin, size - margin, step):
            if random.random() >= 0.5:
                draw.line([(x, y), (x + step, y + step)], fill=color, width=2)
            else:
                draw.line([(x + step, y), (x, y + step)], fill=color, width=2)

def _draw_voronoi(draw, size, color):
    num_points = 10 + int(random.random() * 5)
    points = [(random.randint(0, size), random.randint(0, size)) for _ in range(num_points)]
    line_color = color[:3] if len(color) == 4 else color

    grid = [[0] * size for _ in range(size)]

    for y in range(size):
        for x in range(size):
            min_dist = float('inf')
            for i, (px, py) in enumerate(points):
                dist = (px - x) ** 2 + (py - y) ** 2
                if dist < min_dist:
                    min_dist = dist
                    grid[y][x] = i

    for y in range(size - 1):
        for x in range(size - 1):
            current = grid[y][x]
            if grid[y][x + 1] != current:
                draw.point((x, y), fill=line_color)
            if grid[y + 1][x] != current:
                draw.point((x, y), fill=line_color)

    border_width = 1
    draw.rectangle(
        [(0, 0), (size - 1, size - 1)],
        outline=line_color,
        width=border_width
    )

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
        'hypnotic squares': _draw_hypnotic_squares,
        'tiled lines': _draw_tiled_lines,
        'voronoi': _draw_voronoi,
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
