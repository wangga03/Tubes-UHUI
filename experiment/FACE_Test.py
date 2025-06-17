import os
import pickle
from keras_facenet import FaceNet
import cv2
from sklearn.neighbors import KNeighborsClassifier
import numpy as np
import imgaug.augmenters as iaa
import sys
import contextlib
import gpiod
import time

# === PATH & INISIALISASI ===
pkl_path = '/home/raspiuhui/Tubes-UHUI/HASIL_FACENET/knn_facenet_aug2.pkl'
cascade_path = '/home/raspiuhui/Tubes-UHUI/haarcascade_frontalface_alt2.xml'
dataset_path = '/home/raspiuhui/Tubes-UHUI/dataset3'

# --- suppress stdout dari keras ---
@contextlib.contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout

# --- Inisialisasi FaceNet ---
embedder = FaceNet()

# === INISIALISASI GPIO (gpiod v2) ===
chip = gpiod.Chip("/dev/gpiochip4")
lines = {
    "wggjak": 27,
    "other": 17,
    "none": 22,
}

# Claim ketiga pin sekaligus sebagai output
request = chip.request_lines(
    consumer="face_gpio",
    config=gpiod.LineSettings(direction=gpiod.LineDirection.OUTPUT),
    offsets=[lines["wggjak"], lines["other"], lines["none"]],
)

# Fungsi set GPIO
def set_gpio(wggjak=False, other=False, none=False):
    values = {
        lines["wggjak"]: int(wggjak),
        lines["other"]: int(other),
        lines["none"]: int(none),
    }
    request.set_values(values)

# --- Load model KNN jika ada ---
if os.path.exists(pkl_path):
    print("Memuat model KNN dari file .pkl...")
    with open(pkl_path, 'rb') as f:
        knn = pickle.load(f)
    print("Model KNN siap digunakan!")
else:
    print("File .pkl belum ada, mulai ekstraksi embedding & training...")
    X, y = [], []
    seq = iaa.Sequential([
        iaa.Fliplr(0.5),
        iaa.Affine(rotate=(-10, 10)),
        iaa.Multiply((0.8, 1.2)),
        iaa.AddToHueAndSaturation((-10, 10)),
        iaa.GaussianBlur(sigma=(0, 1.0)),
    ])
    for label in os.listdir(dataset_path):
        folder = os.path.join(dataset_path, label)
        for file in os.listdir(folder):
            img_path = os.path.join(folder, file)
            img = cv2.imread(img_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (160, 160))
            with suppress_stdout():
                emb = embedder.embeddings([img])[0]
            X.append(emb)
            y.append(label)
            for i in range(3):
                aug_img = seq(image=img)
                with suppress_stdout():
                    aug_emb = embedder.embeddings([aug_img])[0]
                X.append(aug_emb)
                y.append(label)
    X = np.array(X)
    y = np.array(y)
    knn = KNeighborsClassifier(n_neighbors=3, metric='euclidean')
    knn.fit(X, y)
    with open(pkl_path, 'wb') as f:
        pickle.dump(knn, f)
    print("Model telah dilatih & disimpan!")

# --- Inisialisasi Kamera & Haar Cascade ---
face_cascade = cv2.CascadeClassifier(cascade_path)
cap = cv2.VideoCapture(0)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
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
                    color = (0,255,0) if pred != 'jawa' else (0,0,255)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                    cv2.putText(frame, f"{pred} ({conf:.2f})", (x, y-10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # === OUTPUT TERMINAL + GPIO ===
        print("\033c", end="")  # Clear terminal
        if pred == 'wgg' or pred == 'jak':
            print(f"\033[32m{pred} (GPIO27 ON)\033[0m", end="\r", flush=True)
            set_gpio(wggjak=True)
        elif pred is None:
            print(f"\033[33mTidak ada wajah terdeteksi (GPIO22 ON)\033[0m", end="\r", flush=True)
            set_gpio(none=True)
        else:
            print(f"\033[36m{pred} (GPIO17 ON)\033[0m", end="\r", flush=True)
            set_gpio(other=True)

except KeyboardInterrupt:
    print("\nDihentikan oleh user.")

finally:
    cap.release()
    cv2.destroyAllWindows()
    set_gpio()  # Reset semua GPIO LOW
    request.release()
