import math

from PIL import Image

dpi = 300
cover_size = (math.ceil(105 * dpi / 25.4), math.ceil(148 * dpi / 25.4))


def main():
    image = Image.new("RGB", cover_size, color=(255, 255, 255))

    image.show()


if __name__ == "__main__":
    main()
