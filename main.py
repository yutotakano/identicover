import math
import random
import numpy as np

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

    points = [
        [position[0], position[1]],
        [position[0] + size, position[1]],
        [position[0] + size, position[1] + size],
        [position[0], position[1] + size],
    ]
    pre_transform = np.array(points)
    transform_matrix = np.array(
        [
            [math.cos(math.radians(rotation)), -math.sin(math.radians(rotation))],
            [math.sin(math.radians(rotation)), math.cos(math.radians(rotation))],
        ]
    )
    transformed_points = np.dot(pre_transform - position, transform_matrix) + position

    draw.polygon(
        transformed_points.tolist(),
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

    points: list[list[float]] = [
        [position[0] + size / 2, position[1]],
        [position[0], position[1] + size * math.sqrt(3) / 2],
        [position[0] + size, position[1] + size * math.sqrt(3) / 2],
    ]

    pre_transform = np.array(points)
    transform_matrix = np.array(
        [
            [math.cos(math.radians(rotation)), -math.sin(math.radians(rotation))],
            [math.sin(math.radians(rotation)), math.cos(math.radians(rotation))],
        ]
    )
    transformed_points = np.dot(pre_transform - position, transform_matrix) + position

    draw.polygon(transformed_points.tolist(), fill=color, outline=None)


if __name__ == "__main__":
    main()
