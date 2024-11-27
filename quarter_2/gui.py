import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import jpype
import jpype.imports
from jpype.types import *
from backend_poc import extract_img, validate

img_path = None
jpype.startJVM(classpath=['core-3.5.3.jar', 'javase-3.5.3.jar'])

def on_close():
    if jpype.isJVMStarted():
        jpype.shutdownJVM()
    root.destroy()

def browse_image():
    global img_path
    filepath = filedialog.askopenfilename()
    if filepath:
        try:
            img_path = filepath
            img = Image.open(filepath)
            img = img.resize((400, 400), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            
            img_label.config(image=img_tk, text="")
            img_label.image = img_tk  # Keep a reference to avoid garbage collection

            return img
        except Exception as e:
            messagebox.showerror("Error", f"Unable to load image: {e}")


def scan():
    global img_path
    if img_label.cget("text") == "Image Viewer":
        messagebox.showerror("Error", "No image selected!")
    else:
        verdict_msg = tk.Toplevel(root)
        verdict_msg.title("Detection Result")
        verdict_msg.geometry("300x100")

        data = extract_img(img_path)
        verdict = validate("model.xz", data)

        if verdict == 0:
            msg = tk.Label(verdict_msg, text="Safe", fg="green", font=("Arial", 14)) 
            msg.pack(pady=20)
        else:
            msg = tk.Label(verdict_msg, text="Quishing detected !!", fg="red", font=("Arial", 14))
            msg.pack(pady=20)

        close_btn = tk.Button(verdict_msg, text="Close", command=verdict_msg.destroy)
        close_btn.pack()


root = tk.Tk()
root.title("QR Code Quishing Detection")
root.geometry("400x300")
root.protocol("WM_DELETE_WINDOW", on_close)

img_frame = tk.Frame(root, bg="gray", width=200, height=200)
img_frame.pack(pady=20)
img_label = tk.Label(img_frame, text="Image Viewer", bg="gray", width=25, height=10)
img_label.pack()

browse_btn = tk.Button(root, text="Browse", command=browse_image)
browse_btn.pack(pady=5)

instructions = tk.Label(
    root,
    text="1. Select a QR code image.\n"
         "2. Check in the image viewer if the QR code is visible.\n"
         "3. Then press Scan to check for Quishing.",
    justify="left",
)
instructions.pack()

scan_btn = tk.Button(root, text="Scan", command=scan)
scan_btn.pack(pady=10)

root.mainloop()
