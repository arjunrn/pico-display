import argparse
import math

from PIL import Image


class EPDColor:
    def __init__(self, rgb, code):
        self.rgb = rgb
        self.code = code


BLACK = EPDColor((0, 0, 0), b"0")
WHITE = EPDColor((255, 255, 255), b"1")
GREEN = EPDColor((67, 138, 28), b"2")
BLUE = EPDColor((100, 64, 255), b"3")
RED = EPDColor((191, 0, 0), b"4")
YELLOW = EPDColor((255, 243, 56), b"5")
ORANGE = EPDColor((232, 126, 0), b"6")

PALETTE = (
    BLACK.rgb + WHITE.rgb + GREEN.rgb + BLUE.rgb + RED.rgb + YELLOW.rgb + ORANGE.rgb
)


def create_parser():
    parser = argparse.ArgumentParser(description="Image maker for ePaper display")
    parser.add_argument("input", type=str)
    parser.add_argument(
        "--destination", type=str, default="image.rawimg", help="output path"
    )
    parser.add_argument(
        "--max-height",
        type=int,
        default=448,
        help="The maximum height of the output image",
    )
    parser.add_argument(
        "--max-width",
        type=int,
        default=600,
        help="The maximum width of the output image",
    )
    parser.add_argument(
        "--verbose",
        default=False,
        help="Show output image details",
        action="store_true",
    )
    return parser


def create_palette_image():
    p_img = Image.new("P", (16, 16))
    p_img.putpalette(PALETTE)
    return p_img


def resize_image(
    input_image: Image, max_width: int, max_height: int, verbose: bool
) -> Image:
    if input_image.height > max_height:
        height = max_height
        width = math.floor((max_height / input_image.height) * input_image.width)
        if verbose:
            print("Height: {} Width: {}".format(height, width))
        input_image = input_image.resize((width, height))
    if input_image.width > max_width:
        width = max_width
        height = math.floor((max_width / input_image.width) * input_image.height)
        input_image = input_image.resize((width, height))
        if verbose:
            print("Height: {} Width: {}".format(height, width))
    return input_image


def adjust_image(image: Image, palette: Image) -> Image:
    conv = image.quantize(palette=palette, dither=Image.Dither.FLOYDSTEINBERG)
    return conv.convert("RGB")


def run(
    image_path: str, max_width: int, max_height: int, destination: str, verbose=False
):
    input_image = Image.open(image_path)
    input_image = resize_image(input_image, max_width, max_height, verbose)
    palette_image = create_palette_image()
    transform_image = adjust_image(input_image, palette_image)
    image_raw = [
        transform_image.width.to_bytes(4, byteorder="big"),
        transform_image.height.to_bytes(4, byteorder="big"),
    ]
    for x in range(transform_image.width):
        for y in range(transform_image.height):
            pixel = transform_image.getpixel((x, y))
            if pixel == BLACK.rgb:
                image_raw.append(BLACK.code)
            elif pixel == WHITE.rgb:
                image_raw.append(WHITE.code)
            elif pixel == RED.rgb:
                image_raw.append(RED.code)
            elif pixel == BLUE.rgb:
                image_raw.append(BLUE.code)
            elif pixel == GREEN.rgb:
                image_raw.append(GREEN.code)
            elif pixel == YELLOW.rgb:
                image_raw.append(YELLOW.code)
            elif pixel == ORANGE.rgb:
                image_raw.append(ORANGE.code)
            else:
                raise RuntimeError("No color match {}".format(pixel))
    with open(destination, "wb") as thumbnail:
        for x in image_raw:
            thumbnail.write(bytes(x))


if __name__ == "__main__":
    args = create_parser().parse_args()
    run(args.input, args.max_width, args.max_height, args.destination, args.verbose)
