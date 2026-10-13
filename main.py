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
    gradient_angle = random.randint(0, 360)
    gradient_start_coeff = 0
    gradient_end_coeff = 1
    gradient_perpendicular_rad = math.radians((gradient_angle + 90) % 360)
    center = (cover_size[0] / 2, cover_size[1] / 2)
    max_height_from_perpendicular_line_to_any_corner = max(
        [
            abs(
                math.cos(gradient_perpendicular_rad) * (center[1] - corner[1])
                - math.sin(gradient_perpendicular_rad) * (center[0] - corner[0])
            )
            for corner in [
                (0, 0),
                (cover_size[0], 0),
                (cover_size[0], cover_size[1]),
                (0, cover_size[1]),
            ]
        ]
    )

    def get_gradient_coeff(x: float, y: float) -> float:
        # Simple linear gradient from start->end coeffs across the image based on the angle
        # It should be min start, max end
        height = math.cos(gradient_perpendicular_rad) * (center[1] - y) - math.sin(
            gradient_perpendicular_rad
        ) * (center[0] - x)
        # Normalize against maximum possible distance and into [0,1] range
        coeff = (height / max_height_from_perpendicular_line_to_any_corner + 1) / 2
        coeff = (
            gradient_end_coeff - gradient_start_coeff
        ) * coeff + gradient_start_coeff
        return max(0, min(1, coeff))

    gradient_affects = random.choices(
        [
            "position",
            "primary_hue",
            "saturation_base",
            "lightness_base",
            "shape_size_base",
            "shape_rotation_max",
            "alpha",
        ],
        k=random.randint(2, 6),
    )

    primary_hue = random.randint(0, 360)
    shape_saturation_base = random.randint(30, 80)
    shape_lightness_base = random.randint(30, 90)
    palette_style = random.choice(["analogous", "complementary", "triadic"])

    def hue_range(hue: float) -> tuple[float, float]:
        return (max(0, min(360, hue - 10)), max(0, min(360, hue + 10)))

    shape = random.choice(["circle", "square", "triangle"])
    shape_size_base = 10 * dpi / 25.4
    shape_count_range = (10, 30)
    shape_rotation_range = (0, random.randint(0, 360))

    image = Image.new("RGB", cover_size, color=(255, 255, 255))

    background_color = ImageColor.getrgb(
        f"hsl({primary_hue}, {shape_saturation_base}%, {96 if shape_lightness_base > 70 else random.choice([8, 96])}%)"
    )
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 0, cover_size[0], cover_size[1]], fill=background_color)

    shape_count = random.randint(*shape_count_range)
    shape_sizes = [
        int(random.uniform(shape_size_base * 1, shape_size_base * 1.5))
        for _ in range(int(max(1, shape_count * 9 / 10)))  # 90%
    ]

    shape_sizes += [
        int(random.uniform(shape_size_base * 4, shape_size_base * 5))
        for _ in range(shape_count - len(shape_sizes))  # rest
    ]

    for size in sorted(shape_sizes, reverse=True):
        shape_size = size
        shape_position = (
            random.uniform(0, cover_size[0]),
            random.uniform(0, cover_size[1]),
        )
        if "position" in gradient_affects and size < shape_size_base * 2:
            # Resample position based on gradient coefficient:
            # if 0 not affected by gradient
            # if 1 pushed by gradient towards the end of the gradient, whichever
            # direction that is including negative direction
            # (only for small shapes)
            gradient_dir = (
                math.cos(math.radians(gradient_angle)),
                math.sin(math.radians(gradient_angle)),
            )
            affectedness = get_gradient_coeff(shape_position[0], shape_position[1])
            shape_position = (
                shape_position[0]
                + gradient_dir[0] * (cover_size[0] - shape_position[0]) * affectedness,
                shape_position[1]
                + gradient_dir[1] * (cover_size[1] - shape_position[1]) * affectedness,
            )

        shape_size *= (
            2 * get_gradient_coeff(shape_position[0], shape_position[1])
            if "shape_size_base" in gradient_affects
            else 1
        )
        min_rotation, max_rotation = shape_rotation_range
        if "shape_rotation_max" in gradient_affects:
            shape_rotation = int(
                max_rotation * get_gradient_coeff(shape_position[0], shape_position[1])
            )
        else:
            shape_rotation = int(
                random.choice(
                    [
                        min_rotation,
                        min_rotation + (max_rotation - min_rotation) / 2,
                        max_rotation,
                    ]
                )
            )

        if palette_style == "analogous":
            shape_hue = random.uniform(
                *hue_range(
                    primary_hue
                    + 40 * get_gradient_coeff(shape_position[0], shape_position[1])
                    - 20
                    if "primary_hue" in gradient_affects
                    else 0
                )
            )
        elif palette_style == "complementary":
            complementary_hue = (
                primary_hue
                + 180
                + (
                    180 * get_gradient_coeff(shape_position[0], shape_position[1])
                    if "primary_hue" in gradient_affects
                    else 0
                )
            ) % 360
            shape_hue = random.uniform(
                *hue_range(random.choice([primary_hue, complementary_hue]))
            )
        elif palette_style == "triadic":
            triadic_hue1 = (
                primary_hue
                + 120
                * (
                    -120 * get_gradient_coeff(shape_position[0], shape_position[1])
                    if "primary_hue" in gradient_affects
                    else 0
                )
            ) % 360
            triadic_hue2 = (
                primary_hue
                + 240
                * (
                    120 * get_gradient_coeff(shape_position[0], shape_position[1])
                    if "primary_hue" in gradient_affects
                    else 0
                )
            ) % 360
            shape_hue = random.uniform(
                *hue_range(random.choice([primary_hue, triadic_hue1, triadic_hue2]))
            )
        else:
            shape_hue = random.uniform(
                *hue_range(
                    primary_hue
                    + (
                        40 * get_gradient_coeff(shape_position[0], shape_position[1])
                        - 20
                        if "primary_hue" in gradient_affects
                        else 0
                    )
                )
            )

        shape_saturation = random.uniform(
            shape_saturation_base
            - 10
            + (
                40 * get_gradient_coeff(shape_position[0], shape_position[1]) - 20
                if "saturation_base" in gradient_affects
                else 0
            ),
            shape_saturation_base
            + 10
            + (
                40 * get_gradient_coeff(shape_position[0], shape_position[1]) - 20
                if "saturation_base" in gradient_affects
                else 0
            ),
        )
        shape_lightness = random.uniform(
            shape_lightness_base
            - 10
            + (
                40 * get_gradient_coeff(shape_position[0], shape_position[1]) - 20
                if "lightness_base" in gradient_affects
                else 0
            ),
            shape_lightness_base
            + 10
            + (
                40 * get_gradient_coeff(shape_position[0], shape_position[1]) - 20
                if "lightness_base" in gradient_affects
                else 0
            ),
        )
        shape_color: tuple[int, int, int] = ImageColor.getrgb(
            f"hsl({int(shape_hue)}, {max(0, min(100, shape_saturation))}%, {max(0, min(100, shape_lightness))}%)"
        )  # type: ignore

        alpha = 255
        if "alpha" in gradient_affects:
            alpha = 155 + int(
                100 * get_gradient_coeff(shape_position[0], shape_position[1])
            )

        shape_color_alpha = (*shape_color, alpha)

        if shape == "circle":
            draw_circle(
                image, shape_position, shape_size, shape_rotation, shape_color_alpha
            )
        elif shape == "square":
            draw_square(
                image, shape_position, shape_size, shape_rotation, shape_color_alpha
            )
        elif shape == "triangle":
            draw_triangle(
                image, shape_position, shape_size, shape_rotation, shape_color_alpha
            )

    return image


def draw_circle(
    image: Image.Image,
    position: tuple[float, float],
    size: float,
    _rotation: int,
    color: tuple[int, int, int] | tuple[int, int, int, int],
):
    draw = ImageDraw.Draw(image, "RGBA")

    draw.circle(position, size, fill=color, outline=None)


def draw_square(
    image: Image.Image,
    position: tuple[float, float],
    size: float,
    rotation: int,
    color: tuple[int, int, int] | tuple[int, int, int, int],
):
    draw = ImageDraw.Draw(image, "RGBA")

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
    position: tuple[float, float],
    size: float,
    rotation: int,
    color: tuple[int, int, int] | tuple[int, int, int, int],
):
    draw = ImageDraw.Draw(image, "RGBA")

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
