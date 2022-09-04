import datetime
import os.path
from io import BytesIO
from os import path
import requests as requests
from PIL import Image, ImageFont, ImageDraw

from image_generators import utils

# http://api.openweathermap.org/data/2.5/weather?q=Berlin&appid=a25569a68f946853b86023b2cb38cae2&units=metric
# https://openweathermap.org/img/wn/10d@2x.png
icon_dir = "weather-icons"
icon_url = "https://openweathermap.org/img/wn/{0:s}@{1:d}x.png"
weather_url = "http://api.openweathermap.org/data/2.5/weather"


def get_weather(api_key: str) -> dict:
    response = requests.get(
        weather_url, params={"q": "Berlin", "appid": api_key, "units": "metric"}
    )
    if not response.ok:
        raise RuntimeError("Failed to get weather: {}".format(response.content))
    return response.json()


def weather_icon(cache_dir: str, icon: str, scale: int) -> Image:
    cache_icon_dir = path.join(cache_dir, icon_dir)
    if not os.path.exists(cache_icon_dir):
        os.mkdir(cache_icon_dir)
    if not os.path.isdir(cache_icon_dir):
        raise RuntimeError("{0:s} is not a directory".format(cache_icon_dir))

    icon_path = path.join(cache_dir, icon_dir, "{0:s}@{1:d}.png".format(icon, scale))
    if path.exists(icon_path) and path.isfile(icon_path):
        return Image.open(icon_path)
    response = requests.get(icon_url.format(icon, scale))
    if not response.ok:
        raise RuntimeError("Failed to get weather icon {}".format(response.content))
    with open(icon_path, "wb") as icon_file:
        icon_file.write(response.content)
    return Image.open(BytesIO(response.content))


def weather_forecast(api_key: str) -> dict:
    response = requests.get(
        "https://api.openweathermap.org/data/2.5/forecast",
        params={"appId": api_key, "units": "metric", "q": "Berlin"},
    )
    if not response.ok:
        raise RuntimeError(
            "failed to get weather forecast: {}".format(response.content)
        )
    return response.json()


def run(cache_dir: str) -> (list, Image):
    apikey = utils.getenv("OPENWEATHER_API_KEY")
    weather = get_weather(apikey)
    temperature = weather["main"]["temp"]
    min_temperature = weather["main"]["temp_min"]
    max_temperature = weather["main"]["temp_max"]
    image = Image.new("RGBA", (600, 248), "WHITE")
    font_large = ImageFont.truetype(
        "fonts/Lora-Regular.ttf", size=40, layout_engine=ImageFont.Layout.RAQM
    )
    font_medium = ImageFont.truetype(
        "fonts/Lora-Regular.ttf", size=30, layout_engine=ImageFont.Layout.RAQM
    )
    font_small = ImageFont.truetype(
        "fonts/Lora-Regular.ttf", size=25, layout_engine=ImageFont.Layout.RAQM
    )
    draw = ImageDraw.Draw(image)
    draw.text(
        (120, 20), text="{:04.2f}°C".format(temperature), font=font_large, fill="PURPLE"
    )
    draw.text(
        (120, 70),
        text="Min: {:04.2f}°C    Max: {:4.2f} °C".format(
            min_temperature, max_temperature
        ),
        font=font_medium,
        fill="GREEN",
    )

    icon_image = weather_icon(cache_dir, weather["weather"][0]["icon"], 4)
    new_image = Image.new("RGBA", icon_image.size, "WHITE")
    new_image.paste(icon_image, (0, 0), icon_image)

    forecast = weather_forecast(apikey)
    items = len(forecast["list"])
    if items > 6:
        items = 6
    weather_time = []
    for i in range(items):
        f = forecast["list"][i]
        w_icon = weather_icon(cache_dir, f["weather"][0]["icon"], 4)
        wn_icon = Image.new("RGBA", w_icon.size, "WHITE")
        wn_icon.paste(w_icon, (0, 0), w_icon)
        wn_icon = wn_icon.resize((75, 75))
        image.paste(wn_icon, (100 * i + 5, 150), wn_icon)

        ts = datetime.datetime.fromtimestamp(f["dt"])
        time = ts.astimezone().strftime("%H")
        draw.text((100 * i + 30, 210), text=time, font=font_small, fill="BLACK")
        temp = f["main"]["temp"]
        temp_str = "{:.1f}°C".format(temp)
        draw.text(
            (100 * i + 15, 130),
            text=temp_str,
            font=font_small,
            fill="BLACK",
        )
        weather_time.append({"temp": temp_str, "time": time})

    new_image.convert("RGB")
    new_image = new_image.resize((100, 100))
    image.paste(new_image, (10, 10), new_image)
    return weather_time, image


if __name__ == "__main__":
    run("").show()
