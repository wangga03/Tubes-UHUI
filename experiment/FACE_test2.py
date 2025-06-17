import os
import pickle
from keras_facenet import FaceNet
import cv2
from sklearn.neighbors import KNeighborsClassifier
import numpy as np
import imgaug.augmenters as iaa
import sys
import contextlib
import lgpio
import time

# --- Fungsi suppress stdout Keras ---
@contextlib.contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout

# --- INISIALISASI FACENET ---
embedder = FaceNet()
pkl_path = '/home/pi/Tubes-UHUI/HASIL_FACENET/knn_facenet_aug4.pkl'

# === Load KNN model jika ada ===
if os.path.exists(pkl_path):
    print("Memuat model KNN dari file .pkl...")
    with open(pkl_path, 'rb') as f:
        knn = pickle.load(f)
    print("Model KNN siap digunakan!")
else:
    print("File .pkl belum ada. Silakan latih model terlebih dahulu.")
    exit(1)

# --- Setup GPIO ---
h = lgpio.gpiochip_open(0)
print(f"Handle GPIO: {h}")  # Memastikan handle valid (integer positif)
if h < 0:
    print("Gagal membuka gpiochip! Jalankan dengan 'sudo' atau cek akses ke /dev/gpiochip0.")
    exit(1)

led_pins = {
    'tidak_terdeteksi': 22,
    'lain': 17,
    'jak_wgg': 27
}

# Mengklaim pin GPIO sebagai output
for pin in led_pins.values():
    lgpio.gpio_claim_output(h, pin, 0)  # Pastikan pin di-claim dengan benar

def update_gpio(status):
    """Update status LED berdasarkan input"""
    # Matikan semua LED dulu
    for pin in led_pins.values():
        print(f"Mematikan LED pada pin {pin}")  # Debug log
        lgpio.gpio_write(h, pin, 0)  # Mematikan LED pada pin
    
    # Aktifkan LED yang sesuai dengan status
    if status in led_pins:
        pin_to_turn_on = led_pins[status]
        print(f"Menyala LED pada pin {pin_to_turn_on}")  # Debug log
        lgpio.gpio_write(h, pin_to_turn_on, 1)  # Menyalakan LED pada pin yang sesuai

# --- Mulai Webcam ---
face_cascade = cv2.CascadeClassifier('/home/pi/Tubes-UHUI/haarcascade_frontalface_alt2.xml')
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.2, 5)

    pred = None
    if len(faces) > 0:
        for (x, y, w, h) in faces:
            face = frame[y:y+h, x:x+w]
            if face.shape[0] > 0 and face.shape[1] > 0:
                img_rgb = cv2.cvtColor(cv2.resize(face, (160, 160)), cv2.COLOR_BGR2RGB)
                with suppress_stdout():
                    emb = embedder.embeddings([img_rgb])[0]
                pred = knn.predict([emb])[0]
                conf = knn.predict_proba([emb]).max()
                color = (0, 255, 0) if pred in ['wgg', 'jak'] else (0, 0, 255)
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                cv2.putText(frame, f"{pred} ({conf:.2f})", (x, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                break  # hanya proses wajah pertama

    # Print status di terminal
    print("\033c", end="")  # Clear terminal
    if pred in ['wgg', 'jak']:
        print(f"\033[32m{pred} terdeteksi → LED GPIO27 ON\033[0m", end="\r")
        update_gpio('jak_wgg')
    elif pred is None:
        print(f"\033[33mTidak ada wajah terdeteksi → LED GPIO22 ON\033[0m", end="\r")
        update_gpio('tidak_terdeteksi')
    else:
        print(f"\033[31m{pred} terdeteksi → LED GPIO17 ON\033[0m", end="\r")
        update_gpio('lain')

# --- Bersihkan ---
cap.release()
cv2.destroyAllWindows()
for pin in led_pins.values():
    lgpio.gpio_write(h, pin, 0)
lgpio.gpiochip_close(h)

