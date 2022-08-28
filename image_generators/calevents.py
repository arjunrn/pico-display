import datetime
import os

import pytz
import requests
import icalendar
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from image_generators import utils


class Event:
    def __init__(
        self, start_ts: datetime.datetime, end_ts: datetime.datetime, summary: str
    ):
        self.start_ts = start_ts
        self.end_ts = end_ts
        self.summary = summary

    def __str__(self):
        if (
            self.start_ts.hour == 0
            and self.start_ts.minute == 0
            and self.end_ts.hour == 0
            and self.end_ts.minute == 0
        ):
            time_str = "{0:s} - {1:s}".format(
                self.start_ts.strftime("%b %d"), self.end_ts.strftime("%b %d")
            )
        else:
            time_str = "{0:s} - {1:s}".format(
                self.start_ts.strftime("%b %d %H:%M"), self.end_ts.strftime("%H:%M")
            )
        shortened_summary = self.summary
        if len(shortened_summary) > 25:
            shortened_summary = "{0:s}...".format(shortened_summary[:22])

        return "{0:22s} {1:25s}".format(time_str, shortened_summary)


def make_ts(ical_dt) -> datetime.datetime:
    if type(ical_dt) == datetime.date:
        ical_dt = datetime.datetime.combine(ical_dt, datetime.datetime.min.time())
    return ical_dt.astimezone()


def cal_image(events):
    image = Image.new("RGBA", (450, 200), "WHITE")
    event_font = ImageFont.truetype("fonts/FiraCode-Light.ttf", size=15)
    draw = ImageDraw.Draw(image)
    for i in range(len(events)):
        e = events[i]
        if i % 2 == 0:
            rect_color = "ORANGE"
            text_color = "BLACK"
        else:
            rect_color = "BLACK"
            text_color = "WHITE"
        draw.rounded_rectangle(
            (5, (38 * i) + 8, 445, (38 * i) + 38), radius=4, fill=rect_color
        )
        draw.text((10, (38 * i) + 13), text=str(e), font=event_font, fill=text_color)
    return image


def run() -> Image:
    ical_url = utils.getenv("ICAL_URL")
    response = requests.get(ical_url)
    if not response.ok:
        raise RuntimeError("Failed to fetch calendar")
    now = datetime.datetime.now(pytz.UTC).astimezone()
    cal = icalendar.Calendar.from_ical(response.content)
    future_events = []
    for component in cal.walk():
        if component.name == "VEVENT":
            start_time = make_ts(component.get("dtstart").dt)
            end_time = make_ts(component.get("dtend", component.get("dtstart")).dt)
            if start_time > now:
                summary = component.get("summary")
                future_events.append(Event(start_time, end_time, summary))
    future_events = sorted(future_events, key=lambda e: e.start_ts)
    return cal_image(future_events[:5])


if __name__ == "__main__":
    run().show()
