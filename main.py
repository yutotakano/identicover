import math
import random

import numpy as np
from PIL import Image, ImageColor, ImageDraw

dpi = 72
cover_size = (math.ceil(105 * dpi / 25.4), math.ceil(148 * dpi / 25.4))
# random.seed(42)


def main():
    image = Image.new(
        "RGB", (cover_size[0] * 4, cover_size[1] * 4), color=(255, 255, 255)
    )
    for i in range(4):
        for j in range(4):
            sub_image = create_image()
            image.paste(sub_image, (i * cover_size[0], j * cover_size[1]))
    image.show()


def create_image():
    primary_hue = random.randint(0, 360)
    shape_saturation_base = random.randint(50, 90)
    shape_lightness_base = random.randint(30, 90)
    palette_style = random.choice(["analogous", "complementary", "triadic"])

    def hue_range(hue: int) -> tuple[int, int]:
        return (max(0, hue - 10), min(360, hue + 10))

    shape = random.choice(["circle", "square", "triangle"])
    shape_size_base = 10 * dpi / 25.4
    shape_count_range = (10, 15)
    shape_rotation_range = (0, random.randint(0, 360))

    image = Image.new("RGB", cover_size, color=(255, 255, 255))

    background_color = ImageColor.getrgb(
        f"hsl({primary_hue}, {random.choice([40, 60])}%, {random.choice([15, 96])}%)"
    )
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 0, cover_size[0], cover_size[1]], fill=background_color)

    shape_count = random.randint(*shape_count_range)
    shape_sizes = [
        int(random.gammavariate(2.5, 1) * shape_size_base) for _ in range(shape_count)
    ]

    for size in sorted(shape_sizes, reverse=True):
        shape_size = size
        if palette_style == "analogous":
            shape_hue = random.randint(*hue_range(primary_hue))
        elif palette_style == "complementary":
            complementary_hue = (primary_hue + 180) % 360
            shape_hue = random.randint(
                *hue_range(random.choice([primary_hue, complementary_hue]))
            )
        elif palette_style == "triadic":
            triadic_hue1 = (primary_hue + 120) % 360
            triadic_hue2 = (primary_hue + 240) % 360
            shape_hue = random.randint(
                *hue_range(random.choice([primary_hue, triadic_hue1, triadic_hue2]))
            )
        else:
            shape_hue = hue_range(primary_hue)

        shape_saturation = random.randint(
            shape_saturation_base - 10, shape_saturation_base + 10
        )
        shape_lightness = random.randint(
            shape_lightness_base - 10, shape_lightness_base + 10
        )
        shape_color = ImageColor.getrgb(
            f"hsl({shape_hue}, {shape_saturation}%, {shape_lightness}%)"
        )
        shape_position = (
            random.randint(-shape_size, cover_size[0]),
            random.randint(-shape_size, cover_size[1]),
        )
        shape_rotation = int(
            random.choice(
                [
                    shape_rotation_range[0],
                    shape_rotation_range[0]
                    + (shape_rotation_range[1] - shape_rotation_range[0]) / 3,
                    shape_rotation_range[0]
                    + (shape_rotation_range[1] - shape_rotation_range[0]) / 3 * 2,
                    shape_rotation_range[1],
                ]
            )
        )

        if shape == "circle":
            draw_circle(image, shape_position, shape_size, shape_rotation, shape_color)
        elif shape == "square":
            draw_square(image, shape_position, shape_size, shape_rotation, shape_color)
        elif shape == "triangle":
            draw_triangle(
                image, shape_position, shape_size, shape_rotation, shape_color
            )

    return image


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
