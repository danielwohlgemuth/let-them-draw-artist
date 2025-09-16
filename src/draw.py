from PIL import Image, ImageColor, ImageDraw


def draw_image(shape, color):
    img = Image.new('RGB', (400, 400), 'white')
    draw = ImageDraw.Draw(img)

    try:
        # https://drafts.csswg.org/css-color-4/#named-colors
        rgb_color = ImageColor.getrgb(color)
    except ValueError:
        rgb_color = (0, 0, 0)

    if shape.lower() == 'square':
        draw.rectangle([100, 100, 300, 300], fill=rgb_color)
    elif shape.lower() == 'circle':
        draw.ellipse([100, 100, 300, 300], fill=rgb_color)

    return img
