from PIL import Image
from qrcodegen import QrCode
import csv
import random

with open('malicious.csv', mode='r', encoding='utf-8') as f:
    dialect = csv.Sniffer().sniff(f.read(1024))
    f.seek(0)

    r = csv.DictReader(f, delimiter=dialect.delimiter)
    for row in r:
        url = row.get("AdresDomeny")

        ec = random.choice([
            QRCode.Ecc.LOW,
            QRCode.Ecc.MEDIUM,
            QRCode.Ecc.QUARTILE,
            QRCode.Ecc.HIGH,
        ])
        qr = QrCode.encode_text(url, ec)

        # Left out for now, no clue how to specify version with this lib.
        #v = random.randint(1, 10)

        img = qr_to_image(qr)
        img_filename = f"generated/malicious_{i+1}.png"

        img.save(img_filename)


def qr_to_image(qr: QrCode, scale: int = 10, border: int = 4) -> Image.Image:
    """Converts a QrCode object into a PIL Image."""
    size = qr.get_size() + border * 2
    img_size = size * scale
    img = Image.new("1", (img_size, img_size), "white")
    pixels = img.load()
    for y in range(qr.get_size()):
        for x in range(qr.get_size()):
            if qr.get_module(x, y):
                for dy in range(scale):
                    for dx in range(scale):
                        px = (x + border) * scale + dx
                        py = (y + border) * scale + dy
                        pixels[px, py] = 0  # Black
    return img
