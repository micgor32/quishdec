import sys
from PIL import Image
from qrcodegen import QrCode
from qrcodegen2 import QrCode as QrCode2
import csv
import random
import os

def qr_to_image_generic(qr, scale: int = 10, border: int = 4, is_rgb: bool = False) -> Image.Image:
    """
    Converts a QrCode object into a PIL Image.
    Handles both monochrome and RGB images.
    """
    size = qr.get_size()
    img_size = (size + border * 2) * scale
    mode = "RGB" if is_rgb else "1"
    bg_color = "white" if is_rgb else 1
    img = Image.new(mode, (img_size, img_size), bg_color)
    pixels = img.load()

    for y in range(size):
        for x in range(size):
            if qr.get_module(x, y):
                for dy in range(scale):
                    for dx in range(scale):
                        px = (x + border) * scale + dx
                        py = (y + border) * scale + dy
                        if is_rgb:
                            pixels[px, py] = (0, 0, 0)  # Black
                        else:
                            pixels[px, py] = 0  # Black
    return img

def generate_qr_codes(rows, output_folder, num_each_type, method):
    """
    Generates QR codes for a given method.
    - rows: List of rows from the CSV.
    - output_folder: Folder to save images.
    - num_each_type: Number of QR codes to generate.
    - method: Specifies which QR generation method to use.
    """
    for i, row in enumerate(rows):
        url = row.get("AdresDomeny")
        if not url:
            continue

        if method == 1:
            ec = random.choice([
                QrCode.Ecc.LOW,
                QrCode.Ecc.MEDIUM,
                QrCode.Ecc.QUARTILE,
                QrCode.Ecc.HIGH,
            ])
            qr = QrCode.encode_text(url, ec)
            img = qr_to_image_generic(qr, scale=10, border=4, is_rgb=False)
        elif method == 2:
            ecl = random.choice([
                QrCode.Ecc.LOW,
                QrCode.Ecc.MEDIUM,
                QrCode.Ecc.QUARTILE,
                QrCode.Ecc.HIGH,
            ])
            qr = QrCode2.encode_text(url, ecl)
            img = qr_to_image_generic(qr, scale=10, border=4, is_rgb=True)

        # Save image
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        img_filename = f"{output_folder}/qrcode_{method}_{i + 1}.png"
        img.save(img_filename)
        print(f"QR Code image saved as {img_filename}")

def main(csv_filename: str, output_folder: str, num_each_type: int = None):
    """
    Reads a list of names from a CSV file and generates QR codes using two different methods.
    Parameters:
    - csv_filename: The name of the input CSV file.
    - output_folder: The folder where the output PNG files will be saved.
    - num_each_type: The number of QR codes to generate for each type.
    """
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

    if len(sys.argv) > 1:
        try:
            num_each_type = int(sys.argv[1]) // 2
        except ValueError:
            print("Invalid number provided. Please enter a valid integer for the total number of QR codes to generate.")
            sys.exit(1)

    main(csv_filename, output_folder, num_each_type)
