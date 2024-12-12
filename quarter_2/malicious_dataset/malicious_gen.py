import sys
from PIL import Image
from qrcodegen import QrCode
import csv
import random
import numpy as np
import os

def qr_to_image_generic(qr, scale=10, border=4, is_rgb=False):
    size = qr.get_size()
    full_size = size + 2 * border

    img_array = np.ones((full_size * scale, full_size * scale), dtype=np.uint8) * 255  # Default to white (255)

    qr_matrix = np.array([[1 if qr.get_module(x, y) else 0 for x in range(size)] for y in range(size)], dtype=np.uint8)
    qr_matrix = np.pad(qr_matrix, pad_width=border, mode='constant', constant_values=0)

    scaled_matrix = np.kron(qr_matrix, np.ones((scale, scale), dtype=np.uint8))

    img_array[:scaled_matrix.shape[0], :scaled_matrix.shape[1]][scaled_matrix == 1] = 0  # Set black pixels (0)

    if is_rgb:
        img_array = np.stack([img_array] * 3, axis=-1)  # Convert grayscale to RGB
        mode = "RGB"
    else:
        mode = "L"

    return Image.fromarray(img_array, mode)


def modified_add_ecc_and_interleave(self, data: bytearray) -> bytes:
    version: int = self._version
    assert len(data) == QrCode._get_num_data_codewords(version, self._errcorlvl)
    numblocks: int = QrCode._NUM_ERROR_CORRECTION_BLOCKS[self._errcorlvl.ordinal][version]
    blockecclen: int = QrCode._ECC_CODEWORDS_PER_BLOCK[self._errcorlvl.ordinal][version]
    rawcodewords: int = QrCode._get_num_raw_data_modules(version) // 8
    numshortblocks: int = numblocks - rawcodewords % numblocks
    shortblocklen: int = rawcodewords // numblocks

    modified_data = bytearray(data)

    index_to_modify = random.randint(0, len(modified_data) - 1)

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


def generate_qr_codes(rows, output_folder, num_each_type, method):

    for i, row in enumerate(rows):
        url = row.get("AdresDomeny")
        if not url:
            continue

        if method == 1:
            ec = random.choice([
                QrCode.Ecc.MEDIUM,
                QrCode.Ecc.QUARTILE,
                QrCode.Ecc.HIGH,
            ])
            qr = QrCode.encode_text(url, ec)
            img = qr_to_image_generic(qr, scale=10, border=4, is_rgb=False)
        elif method == 2:
            ecl = random.choice([
                QrCode.Ecc.MEDIUM,
                QrCode.Ecc.QUARTILE,
                QrCode.Ecc.HIGH,
            ])
            qr = QrCode.encode_text(url, ecl)
            img = qr_to_image_generic(qr, scale=10, border=4, is_rgb=True)

        # Save image
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        img_filename = f"{output_folder}/qrcode_{method}_{i + 1}.png"
        img.save(img_filename)
    

def main(csv_filename: str, output_folder: str, num_each_type: int = None):
    try:
        with open(csv_filename, mode='r', encoding='utf-8') as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.read(1024))
            csvfile.seek(0)

            rows = list(csv.DictReader(csvfile, delimiter=dialect.delimiter))
            total_rows = len(rows)

            if num_each_type is None:
                num_each_type = total_rows // 2

            if num_each_type * 2 > total_rows:
                print(f"Error: Not enough rows in CSV file to generate {num_each_type * 2} QR codes.")
                return

            print("Starting generation using method from the first script...")
            generate_qr_codes(rows[:num_each_type], output_folder, num_each_type, method=1)

            print("Starting generation using method from the second script...")
            generate_qr_codes(rows[num_each_type:num_each_type * 2], output_folder, num_each_type, method=2)

    except FileNotFoundError:
        print(f"Error: File '{csv_filename}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    csv_filename = 'malicious.csv'
    output_folder = 'generated'
    num_each_type = None
    QrCode._add_ecc_and_interleave = modified_add_ecc_and_interleave
    if len(sys.argv) > 1:
        try:
            num_each_type = int(sys.argv[1]) // 2
        except ValueError:
            print("Invalid number provided. Please enter a valid integer for the total number of QR codes to generate.")
            sys.exit(1)

    main(csv_filename, output_folder, num_each_type)
