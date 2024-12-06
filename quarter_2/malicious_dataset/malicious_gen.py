import sys
from PIL import Image
from qrcodegen import QrCode
from qrcodegen2 import QrCode as QrCode2
import csv
import random
import os

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

def qr_to_png(qr: QrCode2, scale: int = 10, border: int = 4) -> Image.Image:
    """
    Converts a QrCode object into a PIL Image.
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
    return image

def main(csv_filename: str, output_folder: str, num_each_type: int = None):
    """
    Reads a list of names from a CSV file and generates QR codes using two different methods.
    The output is divided equally between the two methods based on the specified number.
    Parameters:
    - csv_filename: The name of the input CSV file.
    - output_folder: The folder where the output PNG files will be saved.
    - num_each_type: The number of QR codes to generate for each type.
    """
    try:
        with open(csv_filename, mode='r', encoding='utf-8') as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.read(1024))
            csvfile.seek(0)

            r = list(csv.DictReader(csvfile, delimiter=dialect.delimiter))
            total_rows = len(r)
            
            if num_each_type is None:
                num_each_type = total_rows // 2
            
            if num_each_type * 2 > total_rows:
                print(f"Error: Not enough rows in CSV file to generate {num_each_type * 2} QR codes.")
                return
            
            print("Starting generation using method from the first script...")
            for i in range(num_each_type):
                row = r[i]
                url = row.get("AdresDomeny")
                if not url:
                    continue
                
                # Generate QR code using method from the first script
                ec = random.choice([
                    QrCode.Ecc.LOW,
                    QrCode.Ecc.MEDIUM,
                    QrCode.Ecc.QUARTILE,
                    QrCode.Ecc.HIGH,
                ])
                qr = QrCode.encode_text(url, ec)
                img = qr_to_image(qr)
                
                # Save image
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                img_filename = f"{output_folder}/qrcode_{i + 1}.png"
                img.save(img_filename)
                print(f"QR Code image saved as {img_filename}")
            
            print("Starting generation using method from the second script...")
            for i in range(num_each_type, num_each_type * 2):
                row = r[i]
                url = row.get("AdresDomeny")
                if not url:
                    continue
                
                # Generate QR code using method from the second script
                ecl = QrCode2.Ecc.MEDIUM
                qr = QrCode2.encode_text(url, ecl)
                img = qr_to_png(qr)
                
                # Save image
                img_filename = f"{output_folder}/qrcode_{i + 1}.png"
                img.save(img_filename)
                print(f"QR Code image saved as {img_filename}")
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
