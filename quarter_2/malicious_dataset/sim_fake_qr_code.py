from __future__ import annotations
from PIL import Image  
from qrcodegen2 import QrCode
import random
import csv
import sys

def modified_add_ecc_and_interleave(self, data: bytearray) -> bytes:
    """Returns a new byte string representing the given data with the appropriate error correction
    codewords appended to it, based on this object's version and error correction level."""
    version: int = self._version
    assert len(data) == QrCode._get_num_data_codewords(version, self._errcorlvl)

    # Calculate parameter numbers
    numblocks: int = QrCode._NUM_ERROR_CORRECTION_BLOCKS[self._errcorlvl.ordinal][version]
    blockecclen: int = QrCode._ECC_CODEWORDS_PER_BLOCK[self._errcorlvl.ordinal][version]
    rawcodewords: int = QrCode._get_num_raw_data_modules(version) // 8
    numshortblocks: int = numblocks - rawcodewords % numblocks
    shortblocklen: int = rawcodewords // numblocks

    modified_data = bytearray(data)

    # Randomly select an index to modify
    index_to_modify = random.randint(0, len(modified_data) - 1)

    # Modify the value at the selected index
    modified_data[index_to_modify] = (modified_data[index_to_modify] + 1) % 256  # Ensure it wraps around within byte limits

    blocks: list[bytes] = []
    rsdiv: bytes = QrCode._reed_solomon_compute_divisor(blockecclen)
    k: int = 0

    for i in range(numblocks):
        mdat: bytearray = modified_data[k : k + shortblocklen - blockecclen + (0 if i < numshortblocks else 1)]
        dat: bytearray = data[k : k + shortblocklen - blockecclen + (0 if i < numshortblocks else 1)]
        k += len(dat)
        ecc1: bytes = QrCode._reed_solomon_compute_remainder(mdat, rsdiv)
        ecc2: bytes = QrCode._reed_solomon_compute_remainder(dat, rsdiv)

        # Adjust half_length to ensure it covers the full length in case of an odd length
        half_length = (len(ecc2) + 1) // 2  # This ensures that any remainder is rounded up

        # Combine the first half from ecc1 and the last half from ecc2
        combined_ecc = ecc1[:half_length] + ecc2[-(len(ecc2) - half_length):]

        # Ensure ecc is the same length as ecc2
        ecc: bytes = combined_ecc
        if i < numshortblocks:
            dat.append(0)
            mdat.append(0)
        combined_block = dat + ecc
        blocks.append(combined_block)

    assert k == len(data)

    # Interleave the blocks
    result = bytearray()
    for i in range(len(blocks[0])):
        for (j, blk) in enumerate(blocks):
            # Skip the padding byte in short blocks
            if (i != shortblocklen - blockecclen) or (j >= numshortblocks):
                result.append(blk[i])
    assert len(result) >= rawcodewords

    return result
QrCode._add_ecc_and_interleave = modified_add_ecc_and_interleave


def qr_to_png(qr: QrCode, scale: int = 10, border: int = 4, filename: str = "qrcode.png") -> None:
    """
    Generates a PNG image from a QrCode object.
    Parameters:
    - qr: QrCode object representing the QR Code.
    - scale: The number of pixels per QR module.
    - border: The width of the quiet zone (border) in modules.
    - filename: The name of the output PNG file.
    """
    size = qr.get_size()
    img_size = (size + border * 2) * scale
    image = Image.new("RGB", (img_size, img_size), "white")
    pixels = image.load()

    for y in range(size):
        for x in range(size):
            if qr.get_module(x, y):
                # Calculate pixel position with scaling and border
                for dy in range(scale):
                    for dx in range(scale):
                        px = (x + border) * scale + dx
                        py = (y + border) * scale + dy
                        pixels[px, py] = (0, 0, 0)  # Black
    image.save(filename)
    print(f"QR Code image saved as {filename}")


def main(csv_filename: str, output_folder: str):
    """
    Reads a list of names from a CSV file and generates a QR code for each name.
    Parameters:
    - csv_filename: The name of the input CSV file.
    - output_folder: The folder where the output PNG files will be saved.
    """
    try:
        with open(csv_filename, newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)  # Skip the header if there is one
            for row in reader:
                if row:
                    name = row[0]
                    ecl = QrCode.Ecc.MEDIUM
                    qr = QrCode.encode_text(name, ecl)
                    filename = f"{output_folder}/{name}_qrcode.png"
                    qr_to_png(qr, scale=10, border=4, filename=filename)
    except FileNotFoundError:
        print(f"Error: File '{csv_filename}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python sim_qrcode.py csv_file.csv output_folder")
    else:
        csv_filename = sys.argv[1]
        output_folder = sys.argv[2]
        main(csv_filename, output_folder)
