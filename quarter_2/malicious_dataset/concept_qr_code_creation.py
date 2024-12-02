from PIL import Image
from qrcodegen import QrCode


# Sample data to encode
data = "Hello, World!"

# Error correction level (choose from LOW, MEDIUM, QUARTILE, HIGH)
ecl = QrCode.Ecc.LOW

# Generate the QR code
qr = QrCode.encode_text(data, ecl)


# For example:
# qr = QrCode.encode_text(data, ecl, minversion=1, maxversion=40, mask=-1, boostecl=True)

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

img = qr_to_image(qr)

img.save("qr_code.png")

img.show()
