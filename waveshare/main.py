import epaper

if __name__ == "__main__":

    epd = epaper.EPD_5in65()

    epd.fill(epd.White)

    with open("dashboard.epdimg", "b") as thumbnail:
        width_b = thumbnail.read(4)
        height_b = thumbnail.read(4)
        width = int.from_bytes(width_b, "big")
        height = int.from_bytes(height_b, "big")
        print(width)
        print(height)
        for x in range(width):
            for y in range(height):
                pixel_b = thumbnail.read(1)
                pixel = int.from_bytes(pixel_b, "big")
                epd.pixel(x, y, pixel)

    epd.EPD_5IN65F_Display(epd.buffer)
    epd.delay_ms(500)
    print("Done")

    epd.Sleep()
