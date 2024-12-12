import os
import csv
import random
from PIL import Image, ImageDraw
from qrcodegen import QrCode


def modified_add_ecc_and_interleave(self, data: bytearray) -> bytes:
    version: int = self._version
    assert len(data) == QrCode._get_num_data_codewords(version, self._errcorlvl)

    # Calculate parameter numbers
    numblocks: int = QrCode._NUM_ERROR_CORRECTION_BLOCKS[self._errcorlvl.ordinal][version]
    blockecclen: int = QrCode._ECC_CODEWORDS_PER_BLOCK[self._errcorlvl.ordinal][version]
    rawcodewords: int = QrCode._get_num_raw_data_modules(version) // 8
    numshortblocks: int = numblocks - rawcodewords % numblocks
    shortblocklen: int = rawcodewords // numblocks

    blocks: list[bytes] = []
    rsdiv: bytes = QrCode._reed_solomon_compute_divisor(blockecclen)
    k: int = 0

    for i in range(numblocks):
        dat: bytearray = data[k: k + shortblocklen - blockecclen + (0 if i < numshortblocks else 1)]
        k += len(dat)
        ecc1: bytes = QrCode._reed_solomon_compute_remainder(dat, rsdiv)

        if i < numshortblocks:
            dat.append(0)

        # Introduce a random chance to modify the data (1 in 3 chance)
        if random.random() < 1 / 3:
            # Randomly determine how many bytes to modify (1 to 3)
            num_modifications = random.randint(1, 3)
            for _ in range(num_modifications):
                index_to_modify = random.randint(0, len(dat) - 1)
                dat[index_to_modify] = (dat[index_to_modify] + 1) % 256

        combined_block = dat + ecc1
        blocks.append(combined_block)

    assert k == len(data)

    result = bytearray()
    for i in range(len(blocks[0])):
        for (j, blk) in enumerate(blocks):
            # Skip the padding byte in short blocks
            if (i != shortblocklen - blockecclen) or (j >= numshortblocks):
                result.append(blk[i])

    return result


# Override the _add_ecc_and_interleave method
QrCode._add_ecc_and_interleave = modified_add_ecc_and_interleave


def create_image_from_raw_qr(qr: QrCode, filename: str, box_size: int = 10, border: int = 4):
    size = (qr._size + border * 2) * box_size  # Calculate the full image size
    img = Image.new("RGB", (size, size), "white")  # Create a blank white image
    draw = ImageDraw.Draw(img)
    # Draw QR code modules
    for y in range(qr._size):
        for x in range(qr._size):
            if qr.get_module(x, y):  # Check if the module is dark
                x0 = (x + border) * box_size
                y0 = (y + border) * box_size
                x1 = x0 + box_size
                y1 = y0 + box_size
                draw.rectangle([x0, y0, x1, y1], fill="black")

    img.save(filename)
  


def generate_benign_qr_images():
    os.makedirs("generated", exist_ok=True)

    with open('benign.csv', mode='r') as f:
        r = csv.reader(f)

        for i, row in enumerate(r):
            url = row[0]

            ec = random.choice([
                QrCode.Ecc.LOW,
                QrCode.Ecc.MEDIUM,
                QrCode.Ecc.QUARTILE,
                QrCode.Ecc.HIGH,
            ])

            # Generate raw QR code
            qr = QrCode.encode_text(url, ec)

            # Save the QR code image
            img_filename = f"generated/benign_{i + 1}.png"
            create_image_from_raw_qr(qr, img_filename)



if __name__ == "__main__":
    generate_benign_qr_images()

