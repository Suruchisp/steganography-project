import cv2
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import ntpath  # For getting file name from path

# Function to extract filename from full path
def get_filename(path):
    return ntpath.basename(path) if path else "No file selected"

# Function to select an image
def select_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.bmp")])
    if file_path:
        entry_image_path.delete(0, tk.END)
        entry_image_path.insert(0, get_filename(file_path))
        lbl_selected_image.config(text="Selected Image: " + get_filename(file_path))
        entry_image_path.image_path = file_path  # Store full path internally

# Drag & Drop function
def drop_file(event):
    file_path = event.data.strip("{}")  
    entry_image_path.delete(0, tk.END)
    entry_image_path.insert(0, get_filename(file_path))
    lbl_selected_image.config(text="Selected Image: " + get_filename(file_path))
    entry_image_path.image_path = file_path  

# Function to encode the message
def encode_message():
    img_path = getattr(entry_image_path, "image_path", None)
    msg = entry_message.get()
    password = entry_password.get()

    if not img_path or not msg or not password:
        messagebox.showerror("Error", "Please fill all fields")
        return

    img = cv2.imread(img_path)
    if img is None:
        messagebox.showerror("Error", "Invalid image file")
        return

    h, w, _ = img.shape
    max_chars = (h * w * 3) // 8  

    if len(msg) > max_chars:
        messagebox.showerror("Error", "Message is too long for this image")
        return

    full_msg = password + "|" + msg + "|END"  
    binary_msg = ''.join(format(ord(c), '08b') for c in full_msg)

    if len(binary_msg) > h * w * 3:
        messagebox.showerror("Error", "Message too long for this image")
        return

    idx = 0
    for i in range(h):
        for j in range(w):
            for color in range(3):  
                if idx < len(binary_msg):
                    img[i, j, color] = (img[i, j, color] & ~1) | int(binary_msg[idx])
                    idx += 1
                else:
                    break

    encrypted_path = "encryptedImage.png"
    cv2.imwrite(encrypted_path, img)
    os.system(f"start {encrypted_path}")
    messagebox.showinfo("Success", "Message encrypted successfully!")

# Function to decode the message
def decode_message():
    img_path = getattr(entry_image_path, "image_path", None)
    input_password = entry_password.get()

    if not img_path or not input_password:
        messagebox.showerror("Error", "Please select an image and enter a password")
        return

    img = cv2.imread(img_path)
    if img is None:
        messagebox.showerror("Error", "Invalid image file")
        return

    binary_msg = ""
    h, w, _ = img.shape
    max_bits = (h * w * 3)

    for i in range(h):
        for j in range(w):
            for color in range(3):
                binary_msg += str(img[i, j, color] & 1)

                if len(binary_msg) >= max_bits:
                    break

    chars = [binary_msg[i:i+8] for i in range(0, len(binary_msg), 8)]
    message = ''.join(chr(int(c, 2)) for c in chars)

    if "|END" in message:
        message = message.split("|END")[0]  
    else:
        messagebox.showerror("Error", "Decryption failed. No valid message found.")
        return

    if "|" in message:
        stored_password, secret_msg = message.split('|', 1)
        if stored_password == input_password:
            lbl_decrypted_message.config(text="Decrypted Message: " + secret_msg)
        else:
            messagebox.showerror("Error", "Incorrect password!")
    else:
        messagebox.showerror("Error", "No hidden message found!")

# Create GUI
root = TkinterDnD.Tk()
root.title("Steganography Tool")
root.geometry("700x500")  # Bigger UI

font_style = ("Arial", 12, "bold")

# Image Selection Section
frame_top = tk.Frame(root)
frame_top.pack(pady=10)

tk.Label(frame_top, text="Select Image:", font=font_style).grid(row=0, column=0, padx=10)
entry_image_path = tk.Entry(frame_top, width=30, font=font_style, state="disabled")
entry_image_path.grid(row=0, column=1, padx=10)
btn_browse = tk.Button(frame_top, text="Browse", font=font_style, command=select_image)
btn_browse.grid(row=0, column=2, padx=10)

# Drag & Drop Section
drop_label = tk.Label(root, text="Drag & Drop Image Here", font=font_style, bg="lightgray", width=50, height=2)
drop_label.pack(pady=10)
drop_label.drop_target_register(DND_FILES)
drop_label.dnd_bind('<<Drop>>', drop_file)

# Input Section
frame_middle = tk.Frame(root)
frame_middle.pack(pady=10)

tk.Label(frame_middle, text="Secret Message:", font=font_style).grid(row=0, column=0, padx=10)
entry_message = tk.Entry(frame_middle, width=40, font=font_style)
entry_message.grid(row=0, column=1, padx=10)

tk.Label(frame_middle, text="Password:", font=font_style).grid(row=1, column=0, padx=10)
entry_password = tk.Entry(frame_middle, width=40, font=font_style, show="*")
entry_password.grid(row=1, column=1, padx=10)

# Buttons Section
frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=10)

btn_encrypt = tk.Button(frame_buttons, text="Encrypt", font=font_style, width=15, height=2, command=encode_message)
btn_encrypt.grid(row=0, column=0, padx=20)

btn_decrypt = tk.Button(frame_buttons, text="Decrypt", font=font_style, width=15, height=2, command=decode_message)
btn_decrypt.grid(row=0, column=1, padx=20)

# Label for Selected Image (Bottom)
lbl_selected_image = tk.Label(root, text="Selected Image: None", font=("Arial", 10))
lbl_selected_image.pack(pady=10)

# Label for Decrypted Message
lbl_decrypted_message = tk.Label(root, text="Decrypted Message: ", font=("Arial", 12, "bold"), fg="green")
lbl_decrypted_message.pack(pady=10)

root.mainloop()
