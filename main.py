import math
import random

from PIL import Image, ImageColor, ImageDraw

dpi = 300
cover_size = (math.ceil(105 * dpi / 25.4), math.ceil(148 * dpi / 25.4))
# random.seed(42)

primary_hue = random.randint(0, 360)
hue_range = (primary_hue - 10, primary_hue + 10)
shape = random.choice(["circle", "square", "triangle"])
shape_size_range = (30, 400)
shape_count_range = (10, 60)
shape_rotation_range = (0, random.randint(0, 360))


def main():
    image = Image.new("RGB", cover_size, color=(255, 255, 255))

    background_color = ImageColor.getrgb(f"hsl({primary_hue}, 60%, 98%)")
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 0, cover_size[0], cover_size[1]], fill=background_color)

    for _ in range(random.randint(*shape_count_range)):
        shape_size = random.randint(*shape_size_range)
        shape_hue = random.randint(*hue_range)
        shape_saturation = random.randint(40, 60)
        shape_lightness = random.randint(70, 90)
        shape_color = ImageColor.getrgb(
            f"hsl({shape_hue}, {shape_saturation}%, {shape_lightness}%)"
        )
        shape_position = (
            random.randint(-shape_size, cover_size[0]),
            random.randint(-shape_size, cover_size[1]),
        )
        shape_rotation = random.randint(*shape_rotation_range)

        if shape == "circle":
            draw_circle(image, shape_position, shape_size, shape_rotation, shape_color)
        elif shape == "square":
            draw_square(image, shape_position, shape_size, shape_rotation, shape_color)
        elif shape == "triangle":
            draw_triangle(
                image, shape_position, shape_size, shape_rotation, shape_color
            )
    image.show()


def draw_circle(
    image: Image.Image,
    position: tuple[int, int],
    size: int,
    _rotation: int,
    color: tuple[int, int, int] | tuple[int, int, int, int],
):
    draw = ImageDraw.Draw(image)

    draw.circle(position, size, fill=color, outline=None)


def draw_square(
    image: Image.Image,
    position: tuple[int, int],
    size: int,
    rotation: int,
    color: tuple[int, int, int] | tuple[int, int, int, int],
):
    draw = ImageDraw.Draw(image)

    top_left = position[0]
    top_right = math.cos(math.radians(rotation)) * size + position[0]
    bottom_left = math.sin(math.radians(rotation)) * size + position[1]
    bottom_right = (
        math.cos(math.radians(rotation)) * size + position[0],
        math.sin(math.radians(rotation)) * size + position[1],
    )

    draw.polygon(
        [
            (top_left, position[1]),
            (top_right, position[1]),
            bottom_right,
            (position[0], bottom_left),
        ],
        fill=color,
        outline=None,
    )


def draw_triangle(
    image: Image.Image,
    position: tuple[int, int],
    size: int,
    rotation: int,
    color: tuple[int, int, int] | tuple[int, int, int, int],
):
    draw = ImageDraw.Draw(image)

    point_1 = position
    point_2 = (
        position[0] + math.cos(math.radians(rotation)) * size,
        position[1] + math.sin(math.radians(rotation)) * size,
    )
    point_3 = (
        position[0] + math.cos(math.radians(rotation + 120)) * size,
        position[1] + math.sin(math.radians(rotation + 120)) * size,
    )

    draw.polygon([point_1, point_2, point_3], fill=color, outline=None)


if __name__ == "__main__":
    main()
