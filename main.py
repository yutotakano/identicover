import itertools
import math
import random
import re
import sys
import textwrap
import typing
import unicodedata

import numpy as np
from PIL import Image, ImageColor, ImageDraw, ImageFont, features

dpi = 72
cover_size = (math.ceil(105 * dpi / 25.4), math.ceil(148 * dpi / 25.4))


def main():
    # Generate exemplerary images
    titles = [
        "ホノルル",
        "The widowhood of Queen Victoria",
        "化物屋敷でソロアサシンになりそこねた私がガッツポーズを決めるまで",
        "目覚めたら横浜伊勢佐木町にいた。",
        "【連載版】【書籍化】私生児の言葉",
        "コメット・Ｘ",
        "思い出の牛乳工場",
        "（連載はじめました）身代り金之助",
        "『鉄砲左平次』序にも一つ",
        "神埼歓迎会に於ける演説（五月二十五日於神埼記念舘）",
        "ドレフュー大疑獄とエミール・ゾーラ",
        "菊　食物としての",
        "Ｒｅ：Ｆｗｄ：二十五年間の文人の社会的地位の進歩",
        "And Then There Were None",
    ]

    image = Image.new(
        "RGB", (cover_size[0] * 7, cover_size[1] * 2), color=(255, 255, 255)
    )
    for i in range(7):
        for j in range(2):
            sub_image = create_image(get_first_japanese_noun(titles[i * 2 + j]))
            image.paste(sub_image, (i * cover_size[0], j * cover_size[1]))
    image.show()


def create_image(short_title: str | None = None) -> Image.Image:
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
        k=random.randint(3, 7),
    )

    primary_hue = random.randint(0, 360)
    shape_saturation_base = random.randint(30, 80)
    shape_lightness_base = random.randint(30, 80)
    palette_style = random.choice(["analogous", "complementary", "triadic"])

    def hue_range(hue: float) -> tuple[float, float]:
        return (max(0, min(360, hue - 10)), max(0, min(360, hue + 10)))

    shape = random.choice(["circle", "square", "triangle", "cross", "semicircle"])
    shape_size_base = 10 * dpi / 25.4
    shape_count_range = (20, 30)
    shape_rotation_range = (0, random.randint(0, 360))

    image = Image.new("RGB", cover_size, color=(255, 255, 255))

    background_color_hsl = (
        primary_hue,
        shape_saturation_base,
        92 if shape_lightness_base > 70 else random.choice([13, 92]),
    )
    background_color = ImageColor.getrgb(
        f"hsl({background_color_hsl[0]}, {background_color_hsl[1]}%, {background_color_hsl[2]}%)"
    )
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 0, cover_size[0], cover_size[1]], fill=background_color)

    shape_count = random.randint(*shape_count_range)
    shape_sizes = [
        int(random.uniform(shape_size_base * 0.5, shape_size_base * 1.5))
        for _ in range(int(max(1, shape_count * 9 / 10)))  # 90%
    ]

    shape_sizes += [
        int(random.uniform(shape_size_base * 6, shape_size_base * 7))
        for _ in range(shape_count - len(shape_sizes))  # rest
    ]

    position_distribution = random.choice(
        [
            "uniform",
            "regular",
        ]
    )

    use_outline = random.choice([True, False, False])

    for i, size in enumerate(sorted(shape_sizes, reverse=True)):
        shape_size = size
        if position_distribution == "regular" and shape_size < shape_size_base * 2:
            grid_size = int(math.sqrt(shape_count))
            shape_position = [
                (i % grid_size + 0.5) * cover_size[0] / grid_size,
                (i // grid_size + 0.5) * cover_size[1] / grid_size,
            ]
            # Rotate by gradient with base at center
            shape_position = np.dot(
                shape_position - np.array([cover_size[0] / 2, cover_size[1] / 2]),
                np.array(
                    [
                        [
                            math.cos(math.radians(gradient_angle)),
                            -math.sin(math.radians(gradient_angle)),
                        ],
                        [
                            math.sin(math.radians(gradient_angle)),
                            math.cos(math.radians(gradient_angle)),
                        ],
                    ]
                ),
            ) + np.array([cover_size[0] / 2, cover_size[1] / 2])
        else:
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
            affectedness = (
                2 * get_gradient_coeff(shape_position[0], shape_position[1]) - 1
            )
            shape_position = (
                shape_position[0]
                + gradient_dir[0]
                * affectedness
                * max_height_from_perpendicular_line_to_any_corner,
                shape_position[1]
                + gradient_dir[1]
                * affectedness
                * max_height_from_perpendicular_line_to_any_corner,
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
        outline_width = int(1.5 * dpi / 25.4)

        if shape == "circle":
            draw_circle(
                image,
                shape_position,
                shape_size,
                shape_rotation,
                None if use_outline else shape_color_alpha,
                shape_color_alpha if use_outline else None,
                outline_width,
            )
        elif shape == "square":
            draw_square(
                image,
                shape_position,
                shape_size,
                shape_rotation,
                None if use_outline else shape_color_alpha,
                shape_color_alpha if use_outline else None,
                outline_width,
            )
        elif shape == "triangle":
            draw_triangle(
                image,
                shape_position,
                shape_size,
                shape_rotation,
                None if use_outline else shape_color_alpha,
                shape_color_alpha if use_outline else None,
                outline_width,
            )
        elif shape == "cross":
            draw_cross(
                image,
                shape_position,
                shape_size,
                shape_rotation,
                None if use_outline else shape_color_alpha,
                shape_color_alpha if use_outline else None,
                outline_width,
            )
        elif shape == "semicircle":
            draw_semicircle(
                image,
                shape_position,
                shape_size,
                shape_rotation,
                None if use_outline else shape_color_alpha,
                shape_color_alpha if use_outline else None,
                outline_width,
            )

    # If title was provided, lay it out in a box
    if not short_title:
        return image

    title_orientation = random.choice(["horizontal", "vertical"])
    if not contains_only_japanese(short_title):
        title_orientation = "horizontal"
    box_position = random.choice(
        ["box_position_1", "box_position_2", "box_position_3", "box_position_4"]
    )

    draw_title(
        image,
        short_title,
        title_orientation,
        box_position,
        background_color_hsl,
    )

    return image


def draw_circle(
    image: Image.Image,
    position: tuple[float, float],
    size: float,
    _rotation: int,
    color: tuple[int, int, int] | tuple[int, int, int, int] | None,
    outline: tuple[int, int, int] | tuple[int, int, int, int] | None,
    outline_width: int,
):
    draw = ImageDraw.Draw(image, "RGBA")

    draw.circle(position, size / 2, fill=color, outline=outline, width=outline_width)


def draw_square(
    image: Image.Image,
    position: tuple[float, float],
    size: float,
    rotation: int,
    color: tuple[int, int, int] | tuple[int, int, int, int] | None,
    outline: tuple[int, int, int] | tuple[int, int, int, int] | None,
    outline_width: int,
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
        outline=outline,
        width=outline_width,
    )


def draw_triangle(
    image: Image.Image,
    position: tuple[float, float],
    size: float,
    rotation: int,
    color: tuple[int, int, int] | tuple[int, int, int, int] | None,
    outline: tuple[int, int, int] | tuple[int, int, int, int] | None,
    outline_width: int,
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

    draw.polygon(
        transformed_points.tolist(), fill=color, outline=outline, width=outline_width
    )


def draw_cross(
    image: Image.Image,
    position: tuple[float, float],
    size: float,
    rotation: int,
    color: tuple[int, int, int] | tuple[int, int, int, int] | None,
    outline: tuple[int, int, int] | tuple[int, int, int, int] | None,
    outline_width: int,
):
    cross_width = size / 4
    half_cross_width = cross_width / 2
    draw = ImageDraw.Draw(image, "RGBA")

    points: list[list[float]] = [
        [position[0] + size / 2 - half_cross_width, position[1]],
        [position[0] + size / 2 + half_cross_width, position[1]],
        [
            position[0] + size / 2 + half_cross_width,
            position[1] + size / 2 - half_cross_width,
        ],
        [position[0] + size, position[1] + size / 2 - half_cross_width],
        [position[0] + size, position[1] + size / 2 + half_cross_width],
        [
            position[0] + size / 2 + half_cross_width,
            position[1] + size / 2 + half_cross_width,
        ],
        [position[0] + size / 2 + half_cross_width, position[1] + size],
        [position[0] + size / 2 - half_cross_width, position[1] + size],
        [
            position[0] + size / 2 - half_cross_width,
            position[1] + size / 2 + half_cross_width,
        ],
        [position[0], position[1] + size / 2 + half_cross_width],
        [position[0], position[1] + size / 2 - half_cross_width],
        [
            position[0] + size / 2 - half_cross_width,
            position[1] + size / 2 - half_cross_width,
        ],
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
        transformed_points.tolist(), fill=color, outline=outline, width=outline_width
    )


def draw_semicircle(
    image: Image.Image,
    position: tuple[float, float],
    size: float,
    rotation: int,
    color: tuple[int, int, int] | tuple[int, int, int, int] | None,
    outline: tuple[int, int, int] | tuple[int, int, int, int] | None,
    outline_width: int,
):
    draw = ImageDraw.Draw(image, "RGBA")

    # Calculate the bounding box for the semicircle
    bbox = [
        position[0] - size / 2,
        position[1] - size / 2,
        position[0] + size / 2,
        position[1] + size / 2,
    ]

    # Draw the semicircle (180 degrees)
    draw.pieslice(
        bbox,
        start=rotation - 90,
        end=rotation + 90,
        fill=color,
        outline=outline,
        width=outline_width,
    )


def contains_only_japanese(text: str) -> bool:
    for char in text:
        if unicodedata.east_asian_width(char) not in ("W", "F"):
            return False
    return True


def contains_japanese(text: str) -> bool:
    for char in text:
        if unicodedata.east_asian_width(char) in ("W", "F"):
            return True
    return False


def get_first_japanese_noun(title: str) -> str | None:
    # If no japanese text, use English
    can_use_nagisa = contains_only_japanese(title)

    if not can_use_nagisa:
        return title

    try:
        import nagisa  # type: ignore
    except ImportError:
        return None

    # Ignore things in brackets like 【】
    title = re.sub(r"【.*?】", "", title)

    tagged = nagisa.tagging(title)  # type: ignore
    tagged_words: list[str] = typing.cast(list[str], tagged.words)  # type: ignore
    tagged_postags: list[str] = typing.cast(list[str], tagged.postags)  # type: ignore
    return "".join(
        res[0]
        for res in itertools.takewhile(
            lambda res: res[1] == "名詞",
            itertools.dropwhile(
                lambda res: res[1] != "名詞", zip(tagged_words, tagged_postags)
            ),
        )
    )


def draw_title(
    image: Image.Image,
    title: str,
    orientation: str,
    box_position: str,
    background_color_hsl: tuple[int, int, int],
):
    if not features.check("raqm"):
        print("raqm not available, skipping text")
        return

    font_path = (
        "./assets/HinaMincho-Regular.ttf"
        if contains_japanese(title)
        else "./assets/DINish-Bold.ttf"
    )

    title = textwrap.fill(title, width=15)

    box_color = ImageColor.getrgb(
        f"hsl({background_color_hsl[0]}, {max(0, background_color_hsl[1] - 20)}%, {background_color_hsl[2]}%)"
    )

    is_dark = background_color_hsl[2] < 50
    text_color = ImageColor.getrgb(
        f"hsl({background_color_hsl[0]}, {background_color_hsl[1]}%, {93 if is_dark else 7}%)"
    )

    draw = ImageDraw.Draw(image, "RGBA")

    if orientation == "horizontal":
        # Measure proportions first with arbitrary size
        fnt = ImageFont.truetype(font_path, 40)
        text_bbox = draw.textbbox(
            (0, 0), title, font=fnt, direction="ltr", language="ja"
        )
        h_to_w_ratio = (text_bbox[3] - text_bbox[1]) / (text_bbox[2] - text_bbox[0])
        w = min(cover_size[0] * 0.8, (cover_size[1] * 0.4) / h_to_w_ratio)
        h = w * h_to_w_ratio
        fnt = ImageFont.truetype(font_path, h / len(title.splitlines()))
        # remeasure bbox for accuracy since font size != guaranteed text height
        text_bbox = draw.textbbox(
            (0, 0), title, font=fnt, direction="ltr", language="ja"
        )
        h = text_bbox[3] - text_bbox[1]
        w = text_bbox[2] - text_bbox[0]
        padding = 2 * dpi / 25.4 if contains_japanese(title) else 4 * dpi / 25.4

        if box_position == "box_position_1":
            # Top third
            box = [
                (
                    (cover_size[0] - w) * 0.5 - padding,
                    max(0, cover_size[1] * 0.2 - h * 0.5 - padding),
                ),
                (
                    w + (cover_size[0] - w) * 0.5 + padding,
                    max(h + 2 * padding, cover_size[1] * 0.2 + h * 0.5 + padding),
                ),
            ]
        elif box_position == "box_position_2":
            # Center
            box = [
                (
                    (cover_size[0] - w) * 0.5 - padding,
                    (cover_size[1] - h) * 0.5 - padding,
                ),
                (
                    w + (cover_size[0] - w) * 0.5 + padding,
                    h + (cover_size[1] - h) * 0.5 + padding,
                ),
            ]
        elif box_position == "box_position_3":
            # Bottom third
            box = [
                (
                    (cover_size[0] - w) * 0.5 - padding,
                    min(
                        cover_size[1] - h - 2 * padding,
                        cover_size[1] * 0.8 - h * 0.5 - padding,
                    ),
                ),
                (
                    w + (cover_size[0] - w) * 0.5 + padding,
                    min(
                        cover_size[1],
                        cover_size[1] * 0.8 + h * 0.5 + padding,
                    ),
                ),
            ]
        else:
            # Left aligned, bottom third
            box = [
                (
                    padding,
                    min(
                        cover_size[1] - h - 2 * padding,
                        cover_size[1] * 0.8 - h * 0.5 - padding,
                    ),
                ),
                (
                    float(cover_size[0]),
                    min(
                        cover_size[1],
                        cover_size[1] * 0.8 + h * 0.5 + padding,
                    ),
                ),
            ]
        draw.rectangle(box, fill=box_color)
        draw.multiline_text(
            # Subtract text_bbox offset since ink != position
            (box[0][0] + padding - text_bbox[0], box[0][1] + padding - text_bbox[1]),
            title,
            font=fnt,
            fill=text_color,
            align="center" if box_position != "box_position_4" else "left",
            direction="ltr",
        )
    else:
        # Measure proportions first with arbitrary size
        fnt = ImageFont.truetype(font_path, 40)
        text_bbox = draw.textbbox(
            (0, 0), title, font=fnt, direction="ttb", language="ja"
        )
        h_to_w_ratio = (text_bbox[3] - text_bbox[1]) / (text_bbox[2] - text_bbox[0])
        h = min(cover_size[1] * 0.8, (cover_size[0] * 0.2) * h_to_w_ratio)
        w = h / h_to_w_ratio
        fnt = ImageFont.truetype(font_path, w / len(title.splitlines()))
        # remeasure bbox for accuracy since font size != guaranteed text width
        text_bbox = draw.textbbox(
            (0, 0), title, font=fnt, direction="ttb", language="ja"
        )
        h = text_bbox[3] - text_bbox[1]
        w = text_bbox[2] - text_bbox[0]
        padding = 2 * dpi / 25.4

        if box_position == "box_position_1":
            # Left third
            box = [
                (
                    cover_size[0] * 0.2 - w * 0.5 - padding,
                    (cover_size[1] - h) * 0.5 - padding,
                ),
                (
                    cover_size[0] * 0.2 + w * 0.5 + padding,
                    h + (cover_size[1] - h) * 0.5 + padding,
                ),
            ]
        elif box_position == "box_position_2":
            # Center
            box = [
                (
                    cover_size[0] * 0.5 - w * 0.5 - padding,
                    (cover_size[1] - h) * 0.5 - padding,
                ),
                (
                    cover_size[0] * 0.5 + w * 0.5 + padding,
                    h + (cover_size[1] - h) * 0.5 + padding,
                ),
            ]
        elif box_position == "box_position_3":
            # Right third
            box = [
                (
                    cover_size[0] * 0.8 - w * 0.5 - padding,
                    (cover_size[1] - h) * 0.5 - padding,
                ),
                (
                    cover_size[0] * 0.8 + w * 0.5 + padding,
                    h + (cover_size[1] - h) * 0.5 + padding,
                ),
            ]
        else:
            # Top aligned, left third
            box = [
                (
                    cover_size[0] * 0.2 - w * 0.5 - padding,
                    cover_size[0] * 0.2 - w * 0.5 - padding,
                ),
                (
                    cover_size[0] * 0.2 + w * 0.5 + padding,
                    cover_size[0] * 0.2 - w * 0.5 + h + padding,
                ),
            ]
        draw.rectangle(box, fill=box_color)
        draw.multiline_text(
            # Subtract text_bbox offset since ink != position
            (box[0][0] + padding - text_bbox[0], box[0][1] + padding - text_bbox[1]),
            title,
            font=fnt,
            fill=text_color,
            align="left",
            direction="ttb",
        )


if __name__ == "__main__":
    if len(sys.argv) > 1:
        first_noun = get_first_japanese_noun(sys.argv[1])

        # Title was provided, use that as the seed for reproducibility
        random.seed(sys.argv[1])
        image = create_image(first_noun)
        image.show()
    else:
        main()
