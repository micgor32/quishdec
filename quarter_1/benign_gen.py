import qrcode
import csv

with open('benign.csv', mode='r') as f:
    r = csv.reader(f)
    
    for i, row in enumerate(r):
        url = row[0]

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img_filename = f"benign_{i+1}.png"

        img.save(img_filename)
