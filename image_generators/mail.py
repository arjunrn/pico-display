import imaplib
import re

from PIL import Image, ImageDraw, ImageFont

from image_generators import utils

message_re = re.compile(r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)')
status_re = re.compile(r".* \(MESSAGES (?P<messages>\d+) UNSEEN (?P<unseen>\d+)\)")


def unread_count(imap_ssl: imaplib.IMAP4_SSL) -> int:
    count = 0
    resp_code, directories = imap_ssl.list()
    for directory in directories:
        flags, delimiter, directory_name = message_re.match(directory.decode()).groups()
        dir_status = imap_ssl.status(directory_name, "(MESSAGES UNSEEN)")[1][0]
        _, unseen = status_re.match(dir_status.decode()).groups()
        count += int(unseen)
    return count


def run() -> Image:
    imap_username = utils.getenv("IMAP_USERNAME")
    imap_password = utils.getenv("IMAP_PASSWORD")
    with imaplib.IMAP4_SSL(
        host="imap.mailbox.org", port=imaplib.IMAP4_SSL_PORT
    ) as imap_ssl:
        imap_ssl.login(imap_username, imap_password)
        unread = unread_count(imap_ssl)
        imap_ssl.logout()
    mail_image = Image.new("RGBA", (150, 200), "WHITE")
    mail_draw = ImageDraw.Draw(mail_image)
    raw_mail_icon = Image.open("images/mail-icon.jpg")
    mail_icon = raw_mail_icon.resize((100, 100))
    mail_image.paste(mail_icon, (25, 0))

    outer_x = 95
    outer_y = 15
    outer_size = 30

    inner_x = 99
    inner_y = 19
    inner_size = 23
    mail_draw.ellipse(
        (outer_x, outer_y, outer_x + outer_size, outer_y + outer_size),
        fill="BLUE",
        width=0,
    )
    mail_draw.ellipse(
        (inner_x, inner_y, inner_x + inner_size, inner_y + inner_size),
        fill="RED",
        width=0,
    )
    font_20 = ImageFont.truetype("fonts/FiraCode-SemiBold.ttf", size=15)
    mail_draw.text((105, 22), text=str(unread), fill="WHITE", font=font_20)
    return mail_image


if __name__ == "__main__":
    run().show()
