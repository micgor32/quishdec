import qrcode
import csv
import random

with open('benign.csv', mode='r') as f:
    r = csv.reader(f)
    
    for i, row in enumerate(r):
        url = row[0]

        ec = random.choice([
            qrcode.constants.ERROR_CORRECT_L,
            qrcode.constants.ERROR_CORRECT_M,
            qrcode.constants.ERROR_CORRECT_Q,
            qrcode.constants.ERROR_CORRECT_H, 
        ])
        v = random.randint(1, 10)

        qr = qrcode.QRCode(
            version=v,
            error_correction=ec,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img_filename = f"generated/benign_{i+1}.png"

        img.save(img_filename)
