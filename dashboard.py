import argparse
import json
import os
from os.path import isdir

from PIL import Image
from image_generators.calevents import run as calendar
from image_generators.weather import run as weather
from image_generators.mail import run as mail
from image_translate import run as translate

rendered_path = "combined.jpg"
epdimg_path = "dashboard.epdimg"
summary_path = "summary.json"


def make_parser():
    parser = argparse.ArgumentParser(description="Generate image for epaper display.")
    parser.add_argument(
        "--cache-dir", type=str, default=".cache", help="The cache directory"
    )
    return parser


def run(cache_dir: str):
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)
    if not os.path.isdir(cache_dir):
        raise RuntimeError("{0:s} is not a directory", format(cache_dir))
    combined = Image.new("RGB", (600, 448))
    events, c = calendar()
    wt, w = weather(cache_dir)
    m = mail()
    combined.paste(w, (0, 0))
    combined.paste(c, (0, 248))
    combined.paste(m, (450, 248))

    images_dir = os.path.join(cache_dir, "images")
    if not os.path.exists(images_dir):
        os.mkdir(images_dir)
    full_rendered_path = os.path.join(images_dir, rendered_path)
    full_epdimg_path = os.path.join(images_dir, epdimg_path)
    with open(full_rendered_path, "wb") as image_fp:
        combined.save(image_fp)
    translate(full_rendered_path, 600, 448, full_epdimg_path)
    full_json_path = os.path.join(images_dir, summary_path)
    with open(full_json_path, "w") as summary:
        json.dump({"weather": wt, "events": events}, summary)
    return combined


if __name__ == "__main__":
    args = make_parser().parse_args()
    run(args.cache_dir).show()
